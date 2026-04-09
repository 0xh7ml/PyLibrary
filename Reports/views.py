from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from datetime import datetime, timedelta
from Library.models import *

# Create your views here.
def elibrary_report_view(request):
    # Get filter parameters from request (POST or GET)
    if request.method == 'POST':
        daterange = request.POST.get('daterange', '')
        student_id = request.POST.get('student_id', '')
        year = request.POST.get('year', '')
        page_number = request.POST.get('page', 1)  # Handle page from POST for pagination
    else:
        daterange = request.GET.get('daterange', '')
        student_id = request.GET.get('student_id', '')
        year = request.GET.get('year', '')
        page_number = request.GET.get('page', 1)
    
    # Start with all ELibrarySession objects
    queryset = ELibrarySession.objects.select_related(
        'student__department', 
        'seat', 
        'library_entry'
    ).all()
    
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
    queryset = queryset.order_by('-start_time')
    
    # Pagination - 10 items per page
    paginator = Paginator(queryset, 10)
    page_obj = paginator.get_page(page_number)
    
    # Context for template - pass the paginated queryset directly
    context = {
        'data': page_obj,
        'filter_values': {
            'daterange': daterange,
            'student_id': student_id,
            'year': year,
        }
    }
    return render(request, 'reports/elibrary_report.html', context)

def library_report_view(request):
    # Get filter parameters from request (POST or GET)
    if request.method == 'POST':
        daterange = request.POST.get('daterange', '')
        student_id = request.POST.get('student_id', '')
        year = request.POST.get('year', '')
        page_number = request.POST.get('page', 1)  # Handle page from POST for pagination
    else:
        daterange = request.GET.get('daterange', '')
        student_id = request.GET.get('student_id', '')
        year = request.GET.get('year', '')
        page_number = request.GET.get('page', 1)
    
    # Start with all LibraryEntry objects
    queryset = LibraryEntry.objects.select_related(
        'student__department'
    ).all()
    
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
    queryset = queryset.order_by('-entry_time')
    
    # Pagination - 10 items per page
    paginator = Paginator(queryset, 10)
    page_obj = paginator.get_page(page_number)
    
    # Context for template - pass the paginated queryset directly
    context = {
        'data': page_obj,
        'filter_values': {
            'daterange': daterange,
            'student_id': student_id,
            'year': year,
        }
    }
    return render(request, 'reports/library_report.html', context)