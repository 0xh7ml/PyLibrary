from django.contrib import admin
from django.urls import path

from .views import entry_monitor, service_monitor, student_status, library_stats

urlpatterns = [
    path('', entry_monitor, name='entry_monitor'),
    path('service-monitor/', service_monitor, name='service_monitor'),
    path('api/student-status/', student_status, name='student_status'),
    path('api/library-stats/', library_stats, name='library_stats'),
]