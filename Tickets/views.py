from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404

# Importing the Ticket model
from .models import Ticket

# Create your views here.
def ticket_list(request):
    tickets = Ticket.objects.all()
    return render(request, 'tickets/ticket_list.html', {'data': tickets})

def ticket_add(request):
    if request.method == 'POST':
        issue_type = request.POST.get('issue_type')
        description = request.POST.get('description')
        Ticket.objects.create(issue_type=issue_type, description=description)
        return redirect(reverse_lazy('ticket_list'))
    return render(request, 'tickets/ticket_add.html')

def ticket_edit(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    if request.method == 'POST':
        ticket.issue_type = request.POST.get('issue_type')
        ticket.description = request.POST.get('description')
        ticket.status = request.POST.get('status')
        ticket.save()
        return redirect(reverse_lazy('ticket_list'))
    return render(request, 'tickets/ticket_edit.html', {'ticket': ticket})