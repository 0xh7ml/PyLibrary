from django import forms
from .models import LabSeat, LabTicket


class LabSeatForm(forms.ModelForm):
    class Meta:
        model = LabSeat
        fields = ['pc_no', 'layout_slot', 'status', 'ip_address', 'notes']
        widgets = {
            'pc_no': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Lab PC-01'
            }),
            'layout_slot': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '1-30 slot index',
                'min': '1'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'ip_address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. 192.168.1.101 (optional)'
            }),
            'notes': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Optional hardware/location notes'
            }),
        }


class LabTicketAdminForm(forms.ModelForm):
    class Meta:
        model = LabTicket
        fields = ['title', 'issue_type', 'seat', 'status', 'description', 'admin_notes']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'issue_type': forms.Select(attrs={'class': 'form-select'}),
            'seat': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'admin_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
