from django.urls import path
from . import views

app_name = 'lab'

urlpatterns = [
    # Public Lab User Portal & APIs
    path('', views.lab_portal, name='portal'),
    path('api/pc-layout/', views.lab_pc_layout_api, name='api_pc_layout'),
    path('api/session/', views.api_lab_session, name='api_session'),
    path('api/register/', views.api_lab_registration, name='api_register'),
    path('api/ticket/', views.api_lab_ticket, name='api_ticket'),

    # Lab Admin Portal & Management
    path('admin/', views.lab_dashboard, name='dashboard'),
    path('admin/seats/', views.lab_seat_list, name='seat_list'),
    path('admin/seats/create/', views.lab_seat_create, name='seat_create'),
    path('admin/seats/<int:pk>/edit/', views.lab_seat_update, name='seat_update'),
    path('admin/seats/<int:pk>/delete/', views.lab_seat_delete, name='seat_delete'),
    path('admin/report/', views.lab_report, name='report'),
    path('admin/tickets/', views.lab_ticket_list, name='ticket_list'),
    path('admin/tickets/<int:ticket_id>/edit/', views.lab_ticket_edit, name='ticket_edit'),
]
