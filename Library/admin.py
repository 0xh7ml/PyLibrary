from django.contrib import admin
from .models import Department, Student, Faculty, ElibrarySeat, LibraryEntry, ELibrarySession

# Register your models here.
admin.site.site_header = "PyLibrary Admin"
admin.site.site_title = "PyLibrary Super Admin Portal"
admin.site.index_title = "Welcome to PyLibrary Admin Portal"

# Department Admin
admin.site.register(Department)
admin.site.register(Student)
admin.site.register(Faculty)
admin.site.register(ElibrarySeat)
admin.site.register(LibraryEntry)
admin.site.register(ELibrarySession)