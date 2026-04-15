from django.shortcuts import render
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from datetime import datetime, timedelta, date
from calendar import month_name, monthrange
from collections import defaultdict
from Library.models import *


def _get_request_value(request, key):
    if request.method == 'POST':
        return request.POST.get(key, '')
    return request.GET.get(key, '')


def _build_monthly_rows(queryset, date_field_name, year_int, month_int, department_names):
    filtered_records = queryset.filter(**{
        f'{date_field_name}__year': year_int,
        f'{date_field_name}__month': month_int,
    })

    daily_department_counts = defaultdict(lambda: defaultdict(int))
    daily_totals = defaultdict(int)

    for record in filtered_records:
        record_date = getattr(record, date_field_name).date()
        department_name = record.user_department_name or 'Unknown'
        daily_totals[record_date] += 1
        daily_department_counts[record_date][department_name] += 1

    rows = []
    days_in_month = monthrange(year_int, month_int)[1]
    for day in range(1, days_in_month + 1):
        current_date = date(year_int, month_int, day)
        department_cells = []
        for department_name in department_names:
            department_cells.append({
                'name': department_name,
                'value': daily_department_counts[current_date].get(department_name, 0),
            })
        rows.append({
            'report_date': current_date,
            'total_students': daily_totals.get(current_date, 0),
            'department_cells': department_cells,
        })

    return rows, filtered_records.count()

# Create your views here.
@login_required
def elibrary_report_view(request):
    # Get filter parameters from request (POST or GET)
    daterange = _get_request_value(request, 'daterange')
    student_id = _get_request_value(request, 'student_id')
    year = _get_request_value(request, 'year')
    report_mode = _get_request_value(request, 'report_mode')
    report_year = _get_request_value(request, 'report_year')
    report_month = _get_request_value(request, 'report_month')
    
    # Start with all ELibrarySession objects
    queryset = ELibrarySession.objects.select_related(
        'student__department', 
        'seat', 
        'library_entry'
    ).all()
    
    has_filters = bool(daterange or student_id or year)
    today = timezone.localdate()
    is_monthly_report = report_mode == 'monthly' and report_year and report_month
    department_names = list(Department.objects.order_by('name').values_list('name', flat=True))

    if is_monthly_report:
        try:
            monthly_year = int(report_year)
            monthly_month = int(report_month)
        except ValueError:
            is_monthly_report = False
        else:
            monthly_rows, monthly_total_count = _build_monthly_rows(
                queryset,
                'start_time',
                monthly_year,
                monthly_month,
                department_names,
            )
            context = {
                'data': monthly_rows,
                'department_columns': department_names,
                'total_count': monthly_total_count,
                'report_scope_label': f'{month_name[monthly_month]} {monthly_year}',
                'is_monthly_report': True,
                'filter_values': {
                    'daterange': daterange,
                    'student_id': student_id,
                    'year': year,
                    'report_mode': report_mode,
                    'report_year': report_year,
                    'report_month': report_month,
                }
            }
            return render(request, 'reports/elibrary_report.html', context)

    # Apply date range filter
    if daterange:
        try:
            # Parse daterange format: "MM/DD/YYYY - MM/DD/YYYY"
            start_date_str, end_date_str = daterange.split(' - ')
            start_date = datetime.strptime(start_date_str.strip(), '%m/%d/%Y').date()
            end_date = datetime.strptime(end_date_str.strip(), '%m/%d/%Y').date()
            
            # Filter by date range (start_time field)
            queryset = queryset.filter(
                start_time__date__gte=start_date,
                start_time__date__lte=end_date
            )
        except (ValueError, AttributeError):
            # Invalid date format, ignore filter
            pass
    
    # Apply student ID filter (search across generic FK and legacy FK)
    if student_id:
        student_ct = ContentType.objects.get_for_model(Student)
        faculty_ct = ContentType.objects.get_for_model(Faculty)

        matching_student_ids = Student.objects.filter(
            Q(id_no__icontains=student_id) | Q(name__icontains=student_id)
        ).values_list('id', flat=True)

        matching_faculty_ids = Faculty.objects.filter(
            Q(id_no__icontains=student_id) | Q(name__icontains=student_id)
        ).values_list('id', flat=True)

        queryset = queryset.filter(
            Q(content_type=student_ct, object_id__in=matching_student_ids) |
            Q(content_type=faculty_ct, object_id__in=matching_faculty_ids) |
            Q(student__id_no__icontains=student_id) |
            Q(student__name__icontains=student_id)
        )
    
    # Apply year filter
    if year:
        try:
            year_int = int(year)
            queryset = queryset.filter(start_time__year=year_int)
        except ValueError:
            # Invalid year format, ignore filter
            pass
    
    # Order by most recent first
    if not has_filters:
        queryset = queryset.filter(start_time__date=today)

    queryset = queryset.order_by('-start_time')
    
    # Context for template - return all filtered records (no fixed pagination limit)
    context = {
        'data': queryset,
        'total_count': queryset.count(),
        'report_scope_label': 'Today' if not has_filters else 'Filtered',
        'is_monthly_report': False,
        'filter_values': {
            'daterange': daterange,
            'student_id': student_id,
            'year': year,
            'report_mode': report_mode,
            'report_year': report_year,
            'report_month': report_month,
        }
    }
    return render(request, 'reports/elibrary_report.html', context)

@login_required
def library_report_view(request):
    # Get filter parameters from request (POST or GET)
    daterange = _get_request_value(request, 'daterange')
    student_id = _get_request_value(request, 'student_id')
    year = _get_request_value(request, 'year')
    report_mode = _get_request_value(request, 'report_mode')
    report_year = _get_request_value(request, 'report_year')
    report_month = _get_request_value(request, 'report_month')
    
    # Start with all LibraryEntry objects
    queryset = LibraryEntry.objects.select_related(
        'student__department'
    ).all()
    
    has_filters = bool(daterange or student_id or year)
    today = timezone.localdate()
    is_monthly_report = report_mode == 'monthly' and report_year and report_month
    department_names = list(Department.objects.order_by('name').values_list('name', flat=True))

    if is_monthly_report:
        try:
            monthly_year = int(report_year)
            monthly_month = int(report_month)
        except ValueError:
            is_monthly_report = False
        else:
            monthly_rows, monthly_total_count = _build_monthly_rows(
                queryset,
                'entry_time',
                monthly_year,
                monthly_month,
                department_names,
            )
            context = {
                'data': monthly_rows,
                'department_columns': department_names,
                'total_count': monthly_total_count,
                'report_scope_label': f'{month_name[monthly_month]} {monthly_year}',
                'is_monthly_report': True,
                'filter_values': {
                    'daterange': daterange,
                    'student_id': student_id,
                    'year': year,
                    'report_mode': report_mode,
                    'report_year': report_year,
                    'report_month': report_month,
                }
            }
            return render(request, 'reports/library_report.html', context)

    # Apply date range filter
    if daterange:
        try:
            # Parse daterange format: "MM/DD/YYYY - MM/DD/YYYY"
            start_date_str, end_date_str = daterange.split(' - ')
            start_date = datetime.strptime(start_date_str.strip(), '%m/%d/%Y').date()
            end_date = datetime.strptime(end_date_str.strip(), '%m/%d/%Y').date()
            
            # Filter by date range (entry_time field)
            queryset = queryset.filter(
                entry_time__date__gte=start_date,
                entry_time__date__lte=end_date
            )
        except (ValueError, AttributeError):
            # Invalid date format, ignore filter
            pass
    
    # Apply student ID filter (search across generic FK and legacy FK)
    if student_id:
        student_ct = ContentType.objects.get_for_model(Student)
        faculty_ct = ContentType.objects.get_for_model(Faculty)

        matching_student_ids = Student.objects.filter(
            Q(id_no__icontains=student_id) | Q(name__icontains=student_id)
        ).values_list('id', flat=True)

        matching_faculty_ids = Faculty.objects.filter(
            Q(id_no__icontains=student_id) | Q(name__icontains=student_id)
        ).values_list('id', flat=True)

        queryset = queryset.filter(
            Q(content_type=student_ct, object_id__in=matching_student_ids) |
            Q(content_type=faculty_ct, object_id__in=matching_faculty_ids) |
            Q(student__id_no__icontains=student_id) |
            Q(student__name__icontains=student_id)
        )
    
    # Apply year filter
    if year:
        try:
            year_int = int(year)
            queryset = queryset.filter(entry_time__year=year_int)
        except ValueError:
            # Invalid year format, ignore filter
            pass
    
    # Order by most recent first
    if not has_filters:
        queryset = queryset.filter(entry_time__date=today)

    queryset = queryset.order_by('-entry_time')
    
    # Context for template - return all filtered records (no fixed pagination limit)
    context = {
        'data': queryset,
        'total_count': queryset.count(),
        'report_scope_label': 'Today' if not has_filters else 'Filtered',
        'is_monthly_report': False,
        'filter_values': {
            'daterange': daterange,
            'student_id': student_id,
            'year': year,
            'report_mode': report_mode,
            'report_year': report_year,
            'report_month': report_month,
        }
    }
    return render(request, 'reports/library_report.html', context)