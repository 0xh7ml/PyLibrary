from django.contrib import admin
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget
from .models import Department, Student, Faculty, ElibrarySeat, LibraryEntry, ELibrarySession

# Register your models here.
admin.site.site_header = "PyLibrary Admin"
admin.site.site_title = "PyLibrary Super Admin Portal"
admin.site.index_title = "Welcome to PyLibrary Admin Portal"


class StudentResource(resources.ModelResource):
    """Resource for importing/exporting students from CSV"""
    department = fields.Field(
        column_name='department',
        attribute='department',
        widget=ForeignKeyWidget(Department, 'name')
    )

    class Meta:
        model = Student
        fields = ('id', 'name', 'id_no', 'email', 'department', 'is_blocked')
        export_order = ('id', 'name', 'id_no', 'email', 'department', 'is_blocked')
        import_id_fields = ('id_no',)  # Use id_no as unique identifier for updates


class StudentAdmin(ImportExportModelAdmin):
    """Student admin with import/export functionality"""
    resource_class = StudentResource
    list_display = ('name', 'id_no', 'email', 'department', 'is_blocked')
    search_fields = ('name', 'id_no', 'email')
    list_filter = ('department', 'is_blocked')
    ordering = ('name',)
    actions = ('unblock_selected_students',)
    fieldsets = (
        ('Student Info', {
            'fields': ('name', 'id_no', 'email', 'department')
        }),
        ('Account Control', {
            'fields': ('is_blocked', 'blocked_at', 'block_reason')
        }),
    )
    readonly_fields = ('blocked_at',)

    @admin.action(description='Unblock selected students')
    def unblock_selected_students(self, request, queryset):
        updated = queryset.update(is_blocked=False, blocked_at=None, block_reason='')
        self.message_user(request, f'{updated} student(s) have been unblocked.')


# Department Admin
admin.site.register(Department)
admin.site.register(Student, StudentAdmin)
admin.site.register(Faculty)
admin.site.register(ElibrarySeat)
admin.site.register(LibraryEntry)
admin.site.register(ELibrarySession)