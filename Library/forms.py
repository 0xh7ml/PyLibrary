from django import forms
from django.utils import timezone
from .models import Department, ElibrarySeat, Student

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


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'id_no', 'email', 'department', 'is_blocked', 'block_reason']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter full name',
                'required': True,
            }),
            'id_no': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter ID number',
                'required': True,
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter email address',
            }),
            'department': forms.Select(attrs={
                'class': 'form-control',
                'required': True,
            }),
            'is_blocked': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'block_reason': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Optional reason for block',
            }),
        }
        labels = {
            'id_no': 'Student ID',
            'is_blocked': 'Blocked',
            'block_reason': 'Block Reason',
        }

    def clean(self):
        cleaned_data = super().clean()
        is_blocked = cleaned_data.get('is_blocked')
        block_reason = (cleaned_data.get('block_reason') or '').strip()

        if is_blocked and not block_reason:
            cleaned_data['block_reason'] = 'Blocked manually by admin.'
        if not is_blocked:
            cleaned_data['block_reason'] = ''

        return cleaned_data

    def save(self, commit=True):
        student = super().save(commit=False)

        if student.is_blocked:
            if not student.blocked_at:
                student.blocked_at = timezone.now()
        else:
            student.blocked_at = None
            student.block_reason = ''

        if commit:
            student.save()
        return student