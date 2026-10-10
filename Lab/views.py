import json
import logging
import re
from datetime import timedelta, date
from calendar import monthrange
from collections import defaultdict

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from django.core.paginator import Paginator
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from Library.models import Student, Faculty, Department
from .models import LabSeat, LabSession, LabTicket
from .utils import (
    canonical_lab_seats,
    cleanup_duplicate_lab_seats,
    enforce_midnight_lab_session_policy,
    get_user_by_id,
)
from .forms import LabSeatForm, LabTicketAdminForm

logger = logging.getLogger(__name__)


# ==============================================================================
# PUBLIC LAB PORTAL VIEWS (http://127.0.0.1:8000/lab/)
# ==============================================================================

def lab_portal(request):
    """
    Main Computer Lab Monitor portal.
    Students enter their ID to check-in/select a PC or check-out upon exit.
    """
    enforce_midnight_lab_session_policy()
    cleanup_duplicate_lab_seats()

    canonical_seats = canonical_lab_seats().order_by('layout_slot', 'pc_no')
    total_pcs = canonical_seats.count()
    available_pcs = canonical_seats.filter(status='Available').count()
    in_use_pcs = canonical_seats.filter(status='Reserved').count()
    maintenance_pcs = canonical_seats.filter(status='Maintenance').count()

    # Active session mapping for display
    active_sessions = LabSession.objects.filter(status='Active', end_time__isnull=True).select_related('seat')
    seat_session_map = {}
    for sess in active_sessions:
        seat_session_map[sess.seat_id] = {
            'user_name': sess.user_name,
            'user_id_no': sess.user_id_no,
            'start_time': sess.formatted_start_time,
        }

    seats_layout = []
    for seat in canonical_seats:
        info = seat_session_map.get(seat.id, {})
        seats_layout.append({
            'id': seat.id,
            'pc_no': seat.pc_no,
            'status': seat.status,
            'layout_slot': seat.layout_slot or seat.id,
            'user_name': info.get('user_name', ''),
            'user_id_no': info.get('user_id_no', ''),
            'start_time': info.get('start_time', ''),
        })

    departments = Department.objects.order_by('name')

    context = {
        'total_pcs': total_pcs,
        'available_pcs': available_pcs,
        'in_use_pcs': in_use_pcs,
        'maintenance_pcs': maintenance_pcs,
        'seats_layout': seats_layout,
        'departments': departments,
        'footer_notice': 'Please check out from your PC before leaving the Computer Lab to avoid being locked out.',
    }
    return render(request, 'lab/portal.html', context)


def lab_pc_layout_api(request):
    """API endpoint to get the live real-time state of all lab PCs"""
    enforce_midnight_lab_session_policy()
    cleanup_duplicate_lab_seats()

    canonical_seats = canonical_lab_seats().order_by('layout_slot', 'pc_no')
    active_sessions = LabSession.objects.filter(status='Active', end_time__isnull=True)
    active_map = {sess.seat_id: sess for sess in active_sessions}

    seats_data = []
    for s in canonical_seats:
        sess = active_map.get(s.id)
        seats_data.append({
            'id': s.id,
            'pc_no': s.pc_no,
            'status': s.status,
            'layout_slot': s.layout_slot or s.id,
            'user_name': sess.user_name if sess else None,
            'user_id_no': sess.user_id_no if sess else None,
            'start_time': sess.formatted_start_time if sess else None,
        })

    return JsonResponse({
        'status': 'success',
        'seats': seats_data,
        'available_count': canonical_seats.filter(status='Available').count(),
        'in_use_count': canonical_seats.filter(status='Reserved').count(),
        'maintenance_count': canonical_seats.filter(status='Maintenance').count(),
        'total_count': canonical_seats.count(),
    })


@csrf_exempt
def api_lab_session(request):
    """
    Main check-in/check-out endpoint for the Lab:
    - If user has an active Lab session -> Check out immediately and free seat.
    - If user has no active session:
      - If seat_id provided -> Check in to that seat.
      - If no seat_id provided -> Prompt user to choose from available PCs.
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

    enforce_midnight_lab_session_policy()

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid request JSON'}, status=400)

    student_id = str(data.get('student_id', '')).strip()
    seat_id = data.get('seat_id')

    if not student_id:
        return JsonResponse({'status': 'error', 'message': 'Student/Faculty ID is required'}, status=400)

    user, user_type = get_user_by_id(student_id)
    if not user:
        return JsonResponse({
            'status': 'error',
            'not_found': True,
            'message': f'ID {student_id} not found. Please register below.',
        }, status=404)

    if user_type == 'student' and getattr(user, 'is_blocked', False):
        return JsonResponse({
            'status': 'error',
            'is_blocked': True,
            'message': f'Account blocked: {user.block_reason or "Please contact admin."}',
            'student_name': user.name,
        }, status=403)

    content_type = ContentType.objects.get_for_model(user.__class__)

    try:
        with transaction.atomic():
            # Check for existing active session
            active_session = LabSession.objects.filter(
                content_type=content_type,
                object_id=user.id,
                status='Active',
                end_time__isnull=True,
            ).first()

            if not active_session and user_type == 'student':
                active_session = LabSession.objects.filter(
                    student=user,
                    status='Active',
                    end_time__isnull=True,
                ).first()

            # ----------------------------------------------------
            # 1. Active Session Found -> CHECKOUT
            # ----------------------------------------------------
            if active_session:
                seat_name = active_session.seat.pc_no
                active_session.end_session()

                return JsonResponse({
                    'status': 'success',
                    'action': 'checkout',
                    'message': f'Goodbye, {user.name}! You checked out from {seat_name}. Session: {active_session.duration_display}.',
                    'user_name': user.name,
                    'user_type': user_type,
                    'user_id': user.id_no,
                    'seat_number': seat_name,
                    'duration': active_session.duration_display,
                })

            # ----------------------------------------------------
            # 2. No Active Session -> CHECKIN
            # ----------------------------------------------------
            # Check if seat_id was specified
            if seat_id:
                seat = LabSeat.objects.select_for_update().filter(id=seat_id, status='Available').first()
                if not seat:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Selected PC is no longer available. Please select another PC.',
                    }, status=400)

                # Create Lab Session
                new_session = LabSession.objects.create(
                    content_type=content_type,
                    object_id=user.id,
                    student=user if user_type == 'student' else None,
                    seat=seat,
                    status='Active',
                )
                seat.status = 'Reserved'
                seat.save(update_fields=['status'])

                return JsonResponse({
                    'status': 'success',
                    'action': 'checkin',
                    'message': f'Welcome, {user.name}! You are assigned to {seat.pc_no}.',
                    'user_name': user.name,
                    'user_type': user_type,
                    'user_id': user.id_no,
                    'seat_number': seat.pc_no,
                    'department': user.department.name if user.department else 'N/A',
                })

            # If no seat_id was given, check available seats and prompt selection
            available_seats_count = LabSeat.objects.filter(status='Available').count()
            if available_seats_count == 0:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Sorry, no PCs are currently available in the lab.',
                }, status=400)

            return JsonResponse({
                'status': 'success',
                'action': 'prompt_seat_selection',
                'message': f'Hello {user.name}! Please choose an available PC.',
                'user_name': user.name,
                'user_type': user_type,
                'user_id': user.id,
                'user_id_no': user.id_no,
                'department': user.department.name if user.department else 'N/A',
                'requires_seat_selection': True,
            })

    except Exception as e:
        logger.error(f"Error handling lab session for {student_id}: {str(e)}")
        return JsonResponse({'status': 'error', 'message': f'Server error: {str(e)}'}, status=500)


@csrf_exempt
def api_lab_registration(request):
    """Register student directly from the Lab portal modal"""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid request JSON'}, status=400)

    student_id = str(data.get('student_id', '')).strip()
    name = str(data.get('name', '')).strip()
    email = str(data.get('email', '')).strip().lower()
    department_id = data.get('department_id')

    if not re.fullmatch(r'\d{8}', student_id):
        return JsonResponse({'status': 'error', 'message': 'Please provide an 8-digit student ID.'}, status=400)

    if not name:
        return JsonResponse({'status': 'error', 'message': 'Name is required.'}, status=400)

    if not email:
        return JsonResponse({'status': 'error', 'message': 'Email is required.'}, status=400)

    try:
        validate_email(email)
    except ValidationError:
        return JsonResponse({'status': 'error', 'message': 'Invalid email address.'}, status=400)

    if not department_id:
        return JsonResponse({'status': 'error', 'message': 'Please select a department.'}, status=400)

    if Student.objects.filter(id_no=student_id).exists() or Faculty.objects.filter(id_no=student_id).exists():
        return JsonResponse({'status': 'error', 'message': 'An account with this ID already exists.'}, status=400)

    if Student.objects.filter(email=email).exists() or Faculty.objects.filter(email=email).exists():
        return JsonResponse({'status': 'error', 'message': 'An account with this email already exists.'}, status=400)

    department = Department.objects.filter(id=department_id).first()
    if not department:
        return JsonResponse({'status': 'error', 'message': 'Invalid department.'}, status=400)

    student = Student.objects.create(
        name=name,
        email=email,
        department=department,
        id_no=student_id,
    )

    return JsonResponse({
        'status': 'success',
        'message': f'Student {student.name} registered successfully!',
        'student_id': student.id_no,
        'student_name': student.name,
    })


@csrf_exempt
def api_lab_ticket(request):
    """Submit a ticket for Lab issues from the lab portal"""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)

    user_id_no = str(data.get('student_id', '')).strip()
    title = str(data.get('title', '')).strip()
    description = str(data.get('description', '')).strip()
    issue_type = data.get('issue_type', 'pc_issue')
    seat_id = data.get('seat_id')

    if not user_id_no:
        return JsonResponse({'status': 'error', 'message': 'Your ID number is required.'}, status=400)

    if not title or not description:
        return JsonResponse({'status': 'error', 'message': 'Title and description are required.'}, status=400)

    user, user_type = get_user_by_id(user_id_no)
    if not user:
        return JsonResponse({'status': 'error', 'message': 'User ID not recognized.'}, status=404)

    seat = LabSeat.objects.filter(id=seat_id).first() if seat_id else None
    content_type = ContentType.objects.get_for_model(user.__class__)

    ticket = LabTicket.objects.create(
        title=title,
        description=description,
        issue_type=issue_type,
        seat=seat,
        content_type=content_type,
        object_id=user.id,
        student=user if user_type == 'student' else None,
        status='open',
    )

    return JsonResponse({
        'status': 'success',
        'message': f'Lab Ticket #{ticket.id} submitted successfully! The lab technician has been notified.',
        'ticket_id': ticket.id,
    })


# ==============================================================================
# LAB ADMIN DASHBOARD & MANAGEMENT (http://127.0.0.1:8000/lab/admin/)
# ==============================================================================

@login_required
def lab_dashboard(request):
    """Dedicated Admin Dashboard for Computer Lab"""
    enforce_midnight_lab_session_policy()
    cleanup_duplicate_lab_seats()

    now = timezone.now()
    today = now.date()

    # Live Statistics
    students_in_lab = LabSession.objects.filter(status='Active', end_time__isnull=True).count()
    todays_total_sessions = LabSession.objects.filter(start_time__date=today).count()
    total_students_db = Student.objects.count()

    # Unique users today
    unique_user_keys = set()
    for s in LabSession.objects.filter(start_time__date=today).values('content_type_id', 'object_id', 'student_id'):
        if s['student_id']:
            unique_user_keys.add(('student', s['student_id']))
        elif s['content_type_id'] and s['object_id']:
            unique_user_keys.add((s['content_type_id'], s['object_id']))
    unique_users_today = len(unique_user_keys)

    # PC Status Overview
    canonical_seats = canonical_lab_seats().order_by('layout_slot', 'pc_no')
    total_pcs = canonical_seats.count()
    available_pcs = canonical_seats.filter(status='Available').count()
    in_use_pcs = canonical_seats.filter(status='Reserved').count()
    out_of_service_pcs = canonical_seats.filter(status='Maintenance').count()

    # Active session map for PC visual layout
    active_sessions = LabSession.objects.filter(status='Active', end_time__isnull=True).select_related('seat')
    active_session_map = {}
    for sess in active_sessions:
        active_session_map[sess.seat_id] = {
            'name': sess.user_name,
            'id_no': sess.user_id_no,
            'start_time': sess.formatted_start_time,
            'duration': sess.duration_display,
        }

    dashboard_seats_layout = []
    for seat in canonical_seats:
        info = active_session_map.get(seat.id, {})
        dashboard_seats_layout.append({
            'id': seat.id,
            'pc_no': seat.pc_no,
            'status': seat.status,
            'layout_slot': seat.layout_slot or seat.id,
            'user_name': info.get('name', ''),
            'user_id': info.get('id_no', ''),
            'start_time': info.get('start_time', ''),
            'duration': info.get('duration', ''),
        })

    # 7-Day Usage Analytics
    usage_data = []
    for i in range(7):
        d = today - timedelta(days=6 - i)
        count = LabSession.objects.filter(start_time__date=d).count()
        usage_data.append({
            'date': d.strftime('%a (%d %b)'),
            'count': count,
        })

    week_labels = [day['date'] for day in usage_data]
    week_data = [day['count'] for day in usage_data]
    week_total = sum(week_data)

    # Lab Ticket Statistics
    total_tickets = LabTicket.objects.count()
    open_tickets = LabTicket.objects.filter(status='open').count()
    in_progress_tickets = LabTicket.objects.filter(status='in_progress').count()
    resolved_tickets = LabTicket.objects.filter(status='resolved').count()
    closed_tickets = LabTicket.objects.filter(status='closed').count()

    recent_sessions = LabSession.objects.order_by('-start_time')[:10]

    context = {
        'students_in_lab': students_in_lab,
        'todays_total_sessions': todays_total_sessions,
        'unique_users_today': unique_users_today,
        'total_students_db': total_students_db,
        'total_pcs': total_pcs,
        'available_pcs': available_pcs,
        'in_use_pcs': in_use_pcs,
        'out_of_service_pcs': out_of_service_pcs,
        'dashboard_seats_layout': dashboard_seats_layout,
        'week_labels': week_labels,
        'week_data': week_data,
        'week_total': week_total,
        'total_tickets': total_tickets,
        'open_tickets': open_tickets,
        'in_progress_tickets': in_progress_tickets,
        'resolved_tickets': resolved_tickets,
        'closed_tickets': closed_tickets,
        'recent_sessions': recent_sessions,
        'current_date': today,
        'last_updated': now.strftime('%H:%M:%S'),
    }
    return render(request, 'lab/dashboard.html', context)


# ==============================================================================
# LAB SEAT (PC) MANAGEMENT
# ==============================================================================

@login_required
def lab_seat_list(request):
    """List all Computer Lab PCs with search and status filtering"""
    cleanup_duplicate_lab_seats()
    search = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')

    seats = LabSeat.objects.all()
    if search:
        seats = seats.filter(Q(pc_no__icontains=search) | Q(notes__icontains=search))
    if status_filter:
        seats = seats.filter(status=status_filter)

    seats = seats.order_by('layout_slot', 'pc_no')

    paginator = Paginator(seats, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    all_seats_layout = list(
        LabSeat.objects.order_by('layout_slot', 'pc_no').values('id', 'pc_no', 'status', 'layout_slot')
    )

    context = {
        'seats': page_obj,
        'search': search,
        'status_filter': status_filter,
        'total_count': seats.count(),
        'all_seats_layout': all_seats_layout,
    }
    return render(request, 'lab/seats/seat_list.html', context)


@login_required
def lab_seat_create(request):
    """Create a new Lab PC"""
    requested_slot = request.GET.get('slot', '').strip()
    inferred_slot = int(requested_slot) if requested_slot.isdigit() else None

    if request.method == 'POST':
        form = LabSeatForm(request.POST)
        if form.is_valid():
            seat = form.save()
            messages.success(request, f'Lab PC {seat.pc_no} added successfully!')
            return redirect('lab:seat_list')
    else:
        initial = {}
        if inferred_slot:
            initial['layout_slot'] = inferred_slot
            initial['pc_no'] = f"Lab PC-{inferred_slot:02d}"
        form = LabSeatForm(initial=initial)

    return render(request, 'lab/seats/seat_form.html', {
        'form': form,
        'title': 'Add New Lab PC',
        'action': 'Create',
    })


@login_required
def lab_seat_update(request, pk):
    """Update Lab PC details or status"""
    seat = get_object_or_404(LabSeat, pk=pk)
    if request.method == 'POST':
        form = LabSeatForm(request.POST, instance=seat)
        if form.is_valid():
            form.save()
            messages.success(request, f'Lab PC {seat.pc_no} updated successfully!')
            return redirect('lab:seat_list')
    else:
        form = LabSeatForm(instance=seat)

    return render(request, 'lab/seats/seat_form.html', {
        'form': form,
        'seat': seat,
        'title': f'Edit {seat.pc_no}',
        'action': 'Update',
    })


@login_required
def lab_seat_delete(request, pk):
    """Delete a Lab PC"""
    seat = get_object_or_404(LabSeat, pk=pk)
    if request.method == 'POST':
        name = seat.pc_no
        seat.delete()
        messages.success(request, f'Lab PC {name} removed successfully!')
        return redirect('lab:seat_list')
    return render(request, 'lab/seats/seat_confirm_delete.html', {'seat': seat})


# ==============================================================================
# LAB SESSIONS REPORT & ANALYTICS
# ==============================================================================

@login_required
def lab_report(request):
    """Detailed Computer Lab usage report with daily filters and monthly matrix"""
    daterange = request.GET.get('daterange', '')
    student_id = request.GET.get('student_id', '')
    report_mode = request.GET.get('report_mode', 'daily')
    report_year = request.GET.get('report_year', '')
    report_month = request.GET.get('report_month', '')

    queryset = LabSession.objects.select_related('seat', 'student__department').order_by('-start_time')

    department_names = list(Department.objects.order_by('name').values_list('name', flat=True))
    today = timezone.localdate()

    if report_mode == 'monthly' and report_year and report_month:
        try:
            year_int = int(report_year)
            month_int = int(report_month)
        except ValueError:
            year_int, month_int = today.year, today.month

        filtered = queryset.filter(start_time__year=year_int, start_time__month=month_int)
        daily_dept_counts = defaultdict(lambda: defaultdict(int))
        daily_totals = defaultdict(int)
        monthly_dept_totals = defaultdict(int)

        for s in filtered:
            d = s.start_time.date()
            dept = s.user_department_name or 'Unknown'
            daily_totals[d] += 1
            daily_dept_counts[d][dept] += 1
            monthly_dept_totals[dept] += 1

        rows = []
        days_in_month = monthrange(year_int, month_int)[1]
        for day in range(1, days_in_month + 1):
            cur_d = date(year_int, month_int, day)
            cells = [{'name': name, 'value': daily_dept_counts[cur_d].get(name, 0)} for name in department_names]
            rows.append({
                'report_date': cur_d,
                'total_students': daily_totals.get(cur_d, 0),
                'department_cells': cells,
            })

        dept_totals = [{'name': name, 'value': monthly_dept_totals.get(name, 0)} for name in department_names]

        context = {
            'is_monthly': True,
            'report_mode': 'monthly',
            'report_year': year_int,
            'report_month': month_int,
            'department_names': department_names,
            'monthly_rows': rows,
            'monthly_total': filtered.count(),
            'department_totals': dept_totals,
        }
        return render(request, 'lab/report.html', context)

    # Daily / Range Filter
    if daterange:
        try:
            start_str, end_str = daterange.split(' - ')
            start_date = timezone.datetime.strptime(start_str.strip(), '%Y-%m-%d').date()
            end_date = timezone.datetime.strptime(end_str.strip(), '%Y-%m-%d').date()
            queryset = queryset.filter(start_time__date__gte=start_date, start_time__date__lte=end_date)
        except Exception:
            pass

    if student_id:
        queryset = queryset.filter(
            Q(student__id_no__icontains=student_id) |
            Q(student__name__icontains=student_id)
        )

    paginator = Paginator(queryset, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'is_monthly': False,
        'report_mode': 'daily',
        'sessions': page_obj,
        'daterange': daterange,
        'student_id': student_id,
        'total_count': queryset.count(),
        'department_names': department_names,
        'current_year': today.year,
        'current_month': today.month,
    }
    return render(request, 'lab/report.html', context)


# ==============================================================================
# LAB TICKETS MANAGEMENT
# ==============================================================================

@login_required
def lab_ticket_list(request):
    """View and filter Lab tickets"""
    status_filter = request.GET.get('status', '')
    tickets = LabTicket.objects.select_related('seat').order_by('-created_at')

    if status_filter:
        tickets = tickets.filter(status=status_filter)

    paginator = Paginator(tickets, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'lab/tickets/ticket_list.html', {
        'tickets': page_obj,
        'status_filter': status_filter,
        'open_count': LabTicket.objects.filter(status='open').count(),
        'in_progress_count': LabTicket.objects.filter(status='in_progress').count(),
        'resolved_count': LabTicket.objects.filter(status='resolved').count(),
    })


@login_required
def lab_ticket_edit(request, ticket_id):
    """Edit ticket status or assign resolution notes"""
    ticket = get_object_or_404(LabTicket, id=ticket_id)
    if request.method == 'POST':
        form = LabTicketAdminForm(request.POST, instance=ticket)
        if form.is_valid():
            form.save()
            messages.success(request, f'Lab Ticket #{ticket.id} updated!')
            return redirect('lab:ticket_list')
    else:
        form = LabTicketAdminForm(instance=ticket)

    return render(request, 'lab/tickets/ticket_edit.html', {
        'form': form,
        'ticket': ticket,
    })
