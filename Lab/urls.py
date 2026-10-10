from django.urls import path
from . import views

app_name = 'lab'

urlpatterns = [
    # Public Lab User Terminal & APIs
    path('', views.lab_portal, name='portal'),
    path('pc-layout/', views.lab_pc_layout_html, name='pc_layout'),
    path('api/pc-layout/', views.lab_pc_layout_api, name='api_pc_layout'),
    path('api/session/', views.api_lab_session, name='api_session'),
    path('api/register/', views.api_lab_registration, name='api_register'),
    path('api/ticket/', views.api_lab_ticket, name='api_ticket'),

    # Lab Admin Dashboard
    path('admin/', views.lab_dashboard, name='dashboard'),

    # Visual Lab Workstations & Row Layout Designer
    path('admin/seats/', views.lab_seat_list, name='seat_list'),
    path('admin/rows/create/', views.lab_row_create, name='row_create'),
    path('admin/rows/<int:row_id>/delete/', views.lab_row_delete, name='row_delete'),
    path('admin/rows/<int:row_id>/rename/', views.lab_row_rename, name='row_rename'),
    path('admin/rows/<int:row_id>/add-pc/', views.lab_row_add_pc, name='row_add_pc'),
    path('admin/rows/<int:row_id>/add-space/', views.lab_row_add_space, name='row_add_space'),
    path('admin/seats/<int:seat_id>/toggle-status/', views.lab_seat_toggle_status, name='seat_toggle_status'),
    path('admin/seats/<int:seat_id>/edit/', views.lab_seat_edit, name='seat_edit'),
    path('admin/seats/<int:seat_id>/move/', views.lab_seat_move, name='seat_move'),
    path('admin/seats/<int:seat_id>/delete/', views.lab_seat_delete, name='seat_delete'),

    # Lab Reports & Tickets
    path('admin/report/', views.lab_report, name='report'),
    path('admin/tickets/', views.lab_ticket_list, name='ticket_list'),
    path('admin/tickets/<int:ticket_id>/edit/', views.lab_ticket_edit, name='ticket_edit'),
]
