from django.contrib import admin
from django.urls import path
from .views import ticket_list, ticket_add, ticket_edit

urlpatterns = [
    path('tickets/', ticket_list, name='ticket_list'),
    path('tickets/add/', ticket_add, name='ticket_add'),
    path('tickets/edit/<int:ticket_id>/', ticket_edit, name='ticket_edit'),
]