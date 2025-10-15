from django.urls import path
from . import views

app_name = 'library'

urlpatterns = [
    # Department URLs
    path('departments/', views.department_list, name='department_list'),
    path('departments/create/', views.department_create, name='department_create'),
    path('departments/<int:pk>/edit/', views.department_update, name='department_update'),
    
    # ELibrarySeat URLs
    path('seats/', views.elibrary_seat_list, name='elibrary_seat_list'),
    path('seats/create/', views.elibrary_seat_create, name='elibrary_seat_create'),
    path('seats/<int:pk>/edit/', views.elibrary_seat_update, name='elibrary_seat_update'),
]