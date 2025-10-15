from django import forms
from .models import Department, ElibrarySeat

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter department name',
                'required': True
            })
        }
        labels = {
            'name': 'Department Name'
        }

class ElibrarySeatForm(forms.ModelForm):
    class Meta:
        model = ElibrarySeat
        fields = ['pc_no', 'status']
        widgets = {
            'pc_no': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter PC number (e.g., PC-001)',
                'required': True
            }),
            'status': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            })
        }
        labels = {
            'pc_no': 'PC Number',
            'status': 'Status'
        }