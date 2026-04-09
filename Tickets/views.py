from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required

# Importing the Ticket model
from .models import Ticket
from .utils import send_ticket_status_update_email

# Create your views here.
@login_required
def ticket_list(request):
    tickets = Ticket.objects.all()
    return render(request, 'tickets/ticket_list.html', {'data': tickets})

@login_required
def ticket_add(request):
    if request.method == 'POST':
        issue_type = request.POST.get('issue_type')
        description = request.POST.get('description')
        Ticket.objects.create(issue_type=issue_type, description=description)
        return redirect(reverse_lazy('ticket_list'))
    return render(request, 'tickets/ticket_add.html')

@login_required
def ticket_edit(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    if request.method == 'POST':
        old_status = ticket.status
        ticket.title = request.POST.get('title', ticket.title)
        ticket.issue_type = request.POST.get('issue_type')
        ticket.description = request.POST.get('description')
        ticket.status = request.POST.get('status')
        ticket.save()

        # Send email to student/faculty if status has changed
        new_status = ticket.status
        if old_status != new_status:
            send_ticket_status_update_email(ticket)

        return redirect(reverse_lazy('ticket_list'))
    return render(request, 'tickets/ticket_edit.html', {'ticket': ticket})