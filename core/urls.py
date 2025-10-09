from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('sa/', admin.site.urls),
    path('admin/', include('Auth.urls')),
    path('admin/', include('Dashboard.urls')),
    path('admin/', include('Reports.urls')),
    path('admin/', include('Tickets.urls')),
    path('', include('User.urls')),
]

