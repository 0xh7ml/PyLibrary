from django.contrib import admin
from django.urls import path
from .views import library_report_view, elibrary_report_view
urlpatterns = [
    path('library-report/', library_report_view, name='library_report'),
    path('elibrary-report/', elibrary_report_view, name='elibrary_report'),
]