from django.contrib import admin
from django.urls import path

from .views import *

urlpatterns = [
    path('', entry_monitor, name='entry_monitor'),
    path('service-monitor/', service_monitor, name='service_monitor'),
    path('api/entry-exit/', main_library_handler, name='entry_exit_handler'),
    path('api/service-monitor/', service_monitor_handler, name='service_monitor_handler'),
    path('api/seat-selection/', seat_selection_handler, name='seat_selection_handler'),
    path('pc-layout/', pc_layout, name='pc_layout'),
]