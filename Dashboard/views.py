from django.shortcuts import render
from django.db.models import Count, Q
from django.utils import timezone
from django.contrib.auth.decorators import login_required
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

