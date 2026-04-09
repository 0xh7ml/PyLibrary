from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Department, ElibrarySeat
from .forms import DepartmentForm, ElibrarySeatForm

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