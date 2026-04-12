from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count, Q
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from datetime import datetime, timedelta
from Library.models import LibraryEntry, ELibrarySession, ElibrarySeat, Student
from Tickets.models import Ticket

# Create your views here.
@login_required
def home(request):
    # Get current datetime
    now = timezone.now()
    today = now.date()
    
    # Live Library Statistics
    # Students currently in library (entered but not exited)
    students_in_library = LibraryEntry.objects.filter(
        status='Entered',
        entry_time__date=today
    ).count()
    
    # Students currently using E-Library
    students_using_elibrary = ELibrarySession.objects.filter(
        status='Active',
        start_time__date=today
    ).count()
    
    # Students in main library only (in library but not using e-library)
    main_library_only = students_in_library - students_using_elibrary
    
    # PC Status Overview
    total_pcs = ElibrarySeat.objects.count()
    available_pcs = ElibrarySeat.objects.filter(status='Available').count()
    in_use_pcs = ELibrarySession.objects.filter(status='Active').count()
    out_of_service_pcs = ElibrarySeat.objects.filter(status='Maintenance').count()
    
    # PC Usage Analytics for last 7 days
    usage_data = []
    for i in range(7):
        date = today - timedelta(days=6-i)
        usage_count = ELibrarySession.objects.filter(
            start_time__date=date
        ).count()
        usage_data.append({
            'date': date.strftime('%a'),
            'count': usage_count
        })
    
    # Weekly summary for chart
    week_labels = [day['date'] for day in usage_data]
    week_data = [day['count'] for day in usage_data]
    
    # Ticket Statistics (calculate before using in ticket_data)
    total_tickets = Ticket.objects.count()
    open_tickets = Ticket.objects.filter(status='open').count()
    in_progress_tickets = Ticket.objects.filter(status='in_progress').count()
    resolved_tickets = Ticket.objects.filter(status='resolved').count()
    closed_tickets = Ticket.objects.filter(status='closed').count()
    
    # Recent tickets (today)
    today_tickets = Ticket.objects.filter(created_at__date=today).count()
    
    # Ticket pie chart data (now that variables are defined)
    ticket_labels = ['Open', 'In Progress', 'Resolved', 'Closed']
    ticket_data = [open_tickets, in_progress_tickets, resolved_tickets, closed_tickets]
    
    context = {
        # Live Statistics
        'students_in_library': students_in_library,
        'students_using_elibrary': students_using_elibrary,
        'main_library_only': main_library_only,
        
        # PC Status
        'total_pcs': total_pcs,
        'available_pcs': available_pcs,
        'in_use_pcs': in_use_pcs,
        'out_of_service_pcs': out_of_service_pcs,
        
        # Ticket Statistics
        'total_tickets': total_tickets,
        'open_tickets': open_tickets,
        'in_progress_tickets': in_progress_tickets,
        'resolved_tickets': resolved_tickets,
        'closed_tickets': closed_tickets,
        'today_tickets': today_tickets,
        
        # Chart data
        'week_labels': week_labels,
        'week_data': week_data,
        'ticket_labels': ticket_labels,
        'ticket_data': ticket_data,
        
        # Additional stats
        'current_date': today,
        'last_updated': now.strftime('%H:%M:%S'),
    }
    
    return render(request, 'dashboard/home.html', context)


@login_required
def student_list(request):
    """View to display student list with filtering and block/unblock options"""
    students = Student.objects.all().select_related('department')
    
    # Handle POST request for block/unblock action
    if request.method == 'POST':
        action = request.POST.get('action')
        student_id = request.POST.get('student_id')
        block_reason = request.POST.get('block_reason', '')
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        try:
            if not student_id:
                error_msg = "Student ID is required."
                if is_ajax:
                    return JsonResponse({'status': 'error', 'message': error_msg}, status=400)
                messages.error(request, error_msg)
                return redirect('dashboard:student_list')
            
            student = Student.objects.get(id=student_id)
            
            if action == 'block':
                student.is_blocked = True
                student.blocked_at = timezone.now()
                student.block_reason = block_reason
                student.save()
                success_msg = f"Student {student.name} has been blocked successfully."
                
                if is_ajax:
                    return JsonResponse({
                        'status': 'success',
                        'message': success_msg,
                        'is_blocked': student.is_blocked,
                        'blocked_at': student.blocked_at.isoformat(),
                        'block_reason': student.block_reason
                    })
                messages.success(request, success_msg)
            
            elif action == 'unblock':
                student.is_blocked = False
                student.blocked_at = None
                student.block_reason = ''
                student.save()
                success_msg = f"Student {student.name} has been unblocked successfully."
                
                if is_ajax:
                    return JsonResponse({
                        'status': 'success',
                        'message': success_msg,
                        'is_blocked': student.is_blocked
                    })
                messages.success(request, success_msg)
            
            else:
                error_msg = "Invalid action."
                if is_ajax:
                    return JsonResponse({'status': 'error', 'message': error_msg}, status=400)
                messages.error(request, error_msg)
        
        except Student.DoesNotExist:
            error_msg = "Student not found."
            if is_ajax:
                return JsonResponse({'status': 'error', 'message': error_msg}, status=404)
            messages.error(request, error_msg)
        
        except Exception as e:
            error_msg = f"An error occurred: {str(e)}"
            if is_ajax:
                return JsonResponse({'status': 'error', 'message': error_msg}, status=500)
            messages.error(request, error_msg)
        
        return redirect('dashboard:student_list')
    
    # Handle filtering
    # Filter by block status
    block_status = request.GET.get('block_status')
    if block_status:
        if block_status == 'blocked':
            students = students.filter(is_blocked=True)
        elif block_status == 'unblocked':
            students = students.filter(is_blocked=False)
    
    # Filter by student ID
    student_id = request.GET.get('student_id')
    if student_id:
        students = students.filter(Q(id_no__icontains=student_id) | Q(id__icontains=student_id))
    
    # Filter by student name
    student_name = request.GET.get('student_name')
    if student_name:
        students = students.filter(name__icontains=student_name)
    
    # Filter by department
    department_id = request.GET.get('department')
    if department_id:
        students = students.filter(department_id=department_id)
    
    # Sort by blocked status and then by name
    sort_by = request.GET.get('sort_by', 'name')
    if sort_by == 'status':
        students = students.order_by('-is_blocked', 'name')
    elif sort_by == 'blocked_date':
        students = students.order_by('-blocked_at', 'name')
    else:
        students = students.order_by('name')
    
    # Pagination
    paginator = Paginator(students, 25)  # 25 students per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get all departments for filter dropdown
    from Library.models import Department
    departments = Department.objects.all()
    
    # Statistics
    total_students = Student.objects.count()
    blocked_students = Student.objects.filter(is_blocked=True).count()
    unblocked_students = Student.objects.filter(is_blocked=False).count()
    
    context = {
        'page_obj': page_obj,
        'students': page_obj.object_list,
        'departments': departments,
        'total_students': total_students,
        'blocked_students': blocked_students,
        'unblocked_students': unblocked_students,
        'current_block_status': block_status,
        'current_student_id': student_id,
        'current_student_name': student_name,
        'current_department': department_id,
        'sort_by': sort_by,
    }
    
    return render(request, 'dashboard/student_list.html', context)

