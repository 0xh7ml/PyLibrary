from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Department, ElibrarySeat, Student
from .forms import DepartmentForm, ElibrarySeatForm, StudentForm

# Department CRUD Views
@login_required
def department_list(request):
    """List all departments with search and pagination"""
    search = request.GET.get('search', '')
    departments = Department.objects.all()
    
    if search:
        departments = departments.filter(
            Q(name__icontains=search)
        )
    
    departments = departments.order_by('name')
    
    # Pagination
    paginator = Paginator(departments, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'departments': page_obj,
        'search': search,
        'total_count': departments.count(),
    }
    return render(request, 'library/department_list.html', context)

@login_required
def department_create(request):
    """Create a new department"""
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Department created successfully!')
            return redirect('library:department_list')
    else:
        form = DepartmentForm()
    
    context = {
        'form': form,
        'title': 'Add New Department',
        'action': 'Create'
    }
    return render(request, 'library/department_form.html', context)

@login_required
def department_update(request, pk):
    """Update an existing department"""
    department = get_object_or_404(Department, pk=pk)
    
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            messages.success(request, 'Department updated successfully!')
            return redirect('library:department_list')
    else:
        form = DepartmentForm(instance=department)
    
    context = {
        'form': form,
        'department': department,
        'title': 'Edit Department',
        'action': 'Update'
    }
    return render(request, 'library/department_form.html', context)

# ELibrarySeat CRUD Views
@login_required
def elibrary_seat_list(request):
    """List all e-library seats with search and pagination"""
    search = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    seats = ElibrarySeat.objects.all()
    
    if search:
        seats = seats.filter(
            Q(pc_no__icontains=search)
        )
    
    if status_filter:
        seats = seats.filter(status=status_filter)
    
    seats = seats.order_by('pc_no')
    
    # Pagination
    paginator = Paginator(seats, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    
    context = {
        'elibrary_seats': page_obj,
        'search': search,
        'status_filter': status_filter
    }
    return render(request, 'library/elibrary_seat_list.html', context)

@login_required
def elibrary_seat_create(request):
    """Create a new e-library seat"""
    if request.method == 'POST':
        form = ElibrarySeatForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'E-Library seat created successfully!')
            return redirect('library:elibrary_seat_list')
    else:
        form = ElibrarySeatForm()
    
    context = {
        'form': form,
        'title': 'Add New E-Library Seat',
        'action': 'Create'
    }
    return render(request, 'library/elibrary_seat_form.html', context)

@login_required
def elibrary_seat_update(request, pk):
    """Update an existing e-library seat"""
    seat = get_object_or_404(ElibrarySeat, pk=pk)
    
    if request.method == 'POST':
        form = ElibrarySeatForm(request.POST, instance=seat)
        if form.is_valid():
            form.save()
            messages.success(request, 'E-Library seat updated successfully!')
            return redirect('library:elibrary_seat_list')
    else:
        form = ElibrarySeatForm(instance=seat)
    
    context = {
        'form': form,
        'seat': seat,
        'title': 'Edit E-Library Seat',
        'action': 'Update'
    }
    return render(request, 'library/elibrary_seat_form.html', context)


@login_required
def student_list(request):
    """List all students with search and filters."""
    search = request.GET.get('search', '')
    department_filter = request.GET.get('department', '')
    blocked_filter = request.GET.get('blocked', '')

    students = Student.objects.select_related('department').all()

    if search:
        students = students.filter(
            Q(name__icontains=search) |
            Q(id_no__icontains=search) |
            Q(email__icontains=search)
        )

    if department_filter:
        students = students.filter(department_id=department_filter)

    if blocked_filter in ['true', 'false']:
        students = students.filter(is_blocked=(blocked_filter == 'true'))

    students = students.order_by('name')

    is_filtered = bool(search or department_filter or blocked_filter)
    show_pagination = not is_filtered

    if show_pagination:
        paginator = Paginator(students, 15)
        page_number = request.GET.get('page')
        students_data = paginator.get_page(page_number)
        serial_offset = students_data.start_index() - 1
    else:
        students_data = students
        serial_offset = 0

    context = {
        'students': students_data,
        'search': search,
        'department_filter': department_filter,
        'blocked_filter': blocked_filter,
        'departments': Department.objects.order_by('name'),
        'show_pagination': show_pagination,
        'serial_offset': serial_offset,
    }
    return render(request, 'library/student_list.html', context)


@login_required
def student_create(request):
    """Create a new student."""
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student created successfully!')
            return redirect('library:student_list')
    else:
        form = StudentForm()

    context = {
        'form': form,
        'title': 'Add New Student',
        'action': 'Create',
    }
    return render(request, 'library/student_form.html', context)


@login_required
def student_update(request, pk):
    """Update an existing student."""
    student = get_object_or_404(Student, pk=pk)

    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student updated successfully!')
            return redirect('library:student_list')
    else:
        form = StudentForm(instance=student)

    context = {
        'form': form,
        'student': student,
        'title': 'Edit Student',
        'action': 'Update',
    }
    return render(request, 'library/student_form.html', context)


@login_required
def student_delete(request, pk):
    """Delete a student with confirmation."""
    student = get_object_or_404(Student, pk=pk)

    if request.method == 'POST':
        student_name = student.name
        student.delete()
        messages.success(request, f'Student "{student_name}" deleted successfully!')
        return redirect('library:student_list')

    context = {
        'student': student,
    }
    return render(request, 'library/student_confirm_delete.html', context)


@login_required
@require_POST
def student_toggle_block(request, pk):
    """Block or unblock student quickly from student list."""
    student = get_object_or_404(Student, pk=pk)
    student.is_blocked = not student.is_blocked

    if student.is_blocked:
        student.block_reason = student.block_reason or 'Blocked manually by admin.'
        if not student.blocked_at:
            from django.utils import timezone
            student.blocked_at = timezone.now()
        messages.success(request, f'Student "{student.name}" has been blocked.')
    else:
        student.blocked_at = None
        student.block_reason = ''
        messages.success(request, f'Student "{student.name}" has been unblocked.')

    student.save(update_fields=['is_blocked', 'blocked_at', 'block_reason'])
    return redirect('library:student_list')


@login_required
@require_POST
def student_unblock_all(request):
    """Unblock all blocked students in one action."""
    updated = Student.objects.filter(is_blocked=True).update(
        is_blocked=False,
        blocked_at=None,
        block_reason='',
    )

    if updated:
        messages.success(request, f'{updated} student(s) have been unblocked successfully.')
    else:
        messages.info(request, 'No blocked students found.')

    return redirect('library:student_list')