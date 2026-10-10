from django.contrib import admin
from .models import LabSeat, LabSession, LabTicket


@admin.register(LabSeat)
class LabSeatAdmin(admin.ModelAdmin):
    list_display = ('pc_no', 'layout_slot', 'status', 'ip_address', 'updated_at')
    list_filter = ('status',)
    search_fields = ('pc_no', 'notes')
    ordering = ('layout_slot', 'pc_no')


@admin.register(LabSession)
class LabSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'seat', 'user_name', 'user_id_no', 'user_department_name', 'start_time', 'end_time', 'status')
    list_filter = ('status', 'seat')
    search_fields = ('seat__pc_no', 'student__name', 'student__id_no')
    date_hierarchy = 'start_time'


@admin.register(LabTicket)
class LabTicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'issue_type', 'seat', 'status', 'creator_name', 'created_at')
    list_filter = ('status', 'issue_type')
    search_fields = ('title', 'description')
    date_hierarchy = 'created_at'
