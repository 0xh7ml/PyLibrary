from django.contrib import admin
from django.urls import path

from .views import home, student_list

urlpatterns = [
    path('', home, name='home'),
    path('students/', student_list, name='student_list'),
]