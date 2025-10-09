from django.contrib import admin
from django.urls import path
from .views import demo_report
urlpatterns = [
    path('demo/', demo_report, name='demo_report'),
]