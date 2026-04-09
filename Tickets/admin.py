from django.contrib import admin
from .models import Ticket
from .utils import send_ticket_status_update_email


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'issue_type', 'status', 'creator_name', 'creator_id_no', 'created_at')
    list_filter = ('status', 'issue_type')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at', 'updated_at')

    def save_model(self, request, obj, form, change):
        if change and 'status' in form.changed_data:
            super().save_model(request, obj, form, change)
            send_ticket_status_update_email(obj)
        else:
            super().save_model(request, obj, form, change)