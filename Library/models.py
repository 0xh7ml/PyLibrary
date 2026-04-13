from django.db import models
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

# Create your models here.
class Department(models.Model):
    name = models.CharField(max_length=100)
    
    class Meta:
        verbose_name = "Department"
        verbose_name_plural = "Departments"
        db_table = "tb_departments"
        
    def __str__(self):
        return self.name

class ElibrarySeat(models.Model):
    PC_STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Reserved', 'Reserved'),
        ('Maintenance', 'Maintenance'),
    ]
    pc_no = models.CharField(max_length=50)
    layout_slot = models.PositiveIntegerField(null=True, blank=True, unique=True)
    status = models.CharField(max_length=50, choices=PC_STATUS_CHOICES, default='Available')

    class Meta:
        verbose_name = "E-Library Seat"
        verbose_name_plural = "E-Library Seats"
        db_table = "tb_elibraries_seats"

    def __str__(self):
        return f"{self.pc_no}"
    
class Student(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    id_no = models.CharField(max_length=50, unique=True)
    is_blocked = models.BooleanField(default=False)
    blocked_at = models.DateTimeField(null=True, blank=True)
    block_reason = models.CharField(max_length=255, blank=True, default='')

    class Meta:
        verbose_name = "Student"
        verbose_name_plural = "Students"
        db_table = "tb_students"

    def __str__(self):
        return f"{self.name} ({self.id_no})"

class Faculty(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    id_no = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name = "Faculty"
        verbose_name_plural = "Faculty"
        db_table = "tb_faculty"

    def __str__(self):
        return f"{self.name} ({self.id_no})"

class LibraryEntry(models.Model):
    """Track main library entry/exit"""
    ENTRY_STATUS_CHOICES = [
        ('Entered', 'Entered'),
        ('Exited', 'Exited'),
    ]
    
    # Generic foreign key to support both Student and Faculty
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    user = GenericForeignKey('content_type', 'object_id')
    
    # Legacy field for backward compatibility - will be deprecated
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True)
    
    entry_time = models.DateTimeField(auto_now_add=True)
    exit_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=ENTRY_STATUS_CHOICES, default='Entered')
    
    class Meta:
        verbose_name = "Library Entry"
        verbose_name_plural = "Library Entries"
        db_table = "tb_library_entries"
        ordering = ['-entry_time']

    def __str__(self):
        user_name = self.user.name if self.user else (self.student.name if self.student else "Unknown")
        return f"{user_name} - {self.entry_time.strftime('%Y-%m-%d %H:%M')}"
    
    def mark_exit(self):
        """Mark the exit time and change status"""
        self.exit_time = timezone.now()
        self.status = 'Exited'
        self.save()
        
    @property
    def duration(self):
        """Calculate duration spent in library"""
        if self.exit_time:
            return str(self.exit_time - self.entry_time).split('.')[0]  # Return duration without microseconds
        return None

    @property
    def user_name(self):
        """Get the user's name (Student or Faculty)"""
        if self.user:
            return self.user.name
        elif self.student:
            return self.student.name
        return "Unknown"
    
    @property
    def user_id_no(self):
        """Get the user's ID number (Student or Faculty)"""
        if self.user:
            return self.user.id_no
        elif self.student:
            return self.student.id_no
        return "Unknown"
    
    @property
    def user_type(self):
        """Get the user type (Student or Faculty)"""
        if self.user:
            return self.content_type.model.capitalize()
        elif self.student:
            return "Student"
        return "Unknown"

class ELibrarySession(models.Model):
    """Track e-library seat usage sessions"""
    SESSION_STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Exited', 'Exited'),
    ]
    
    # Generic foreign key to support both Student and Faculty
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    user = GenericForeignKey('content_type', 'object_id')
    
    # Legacy field for backward compatibility - will be deprecated
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True)
    
    seat = models.ForeignKey(ElibrarySeat, on_delete=models.CASCADE)
    library_entry = models.ForeignKey(LibraryEntry, on_delete=models.CASCADE, null=True, blank=True)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=SESSION_STATUS_CHOICES, default='Active')

    class Meta:
        verbose_name = "E-Library Session"
        verbose_name_plural = "E-Library Sessions"
        db_table = "tb_elibrary_sessions"
        ordering = ['-start_time']

    def __str__(self):
        user_name = self.user.name if self.user else (self.student.name if self.student else "Unknown")
        return f"{user_name} - {self.seat.pc_no} - {self.start_time.strftime('%Y-%m-%d %H:%M')}"
    
    def end_session(self):
        """End the e-library session"""
        self.end_time = timezone.now()
        self.status = 'Exited'
        self.seat.status = 'Available'
        self.seat.save()
        self.save()
        
    @property
    def duration(self):
        """Calculate duration spent in e-library"""
        if self.end_time:
            return self.end_time - self.start_time
        return None
    
    @property 
    def duration_display(self):
        """Get formatted duration string for display"""
        if self.end_time:
            duration = self.end_time - self.start_time
            return str(duration).split('.')[0]  # Remove microseconds
        return 'Active'
    
    @property
    def formatted_start_time(self):
        """Get formatted start time for display"""
        return self.start_time.strftime('%Y-%m-%d %H:%M:%S')
    
    @property 
    def formatted_end_time(self):
        """Get formatted end time for display"""
        return self.end_time.strftime('%Y-%m-%d %H:%M:%S') if self.end_time else 'Not Exited'
    
    @property
    def user_name(self):
        """Get the user's name (Student or Faculty)"""
        if self.user:
            return self.user.name
        elif self.student:
            return self.student.name
        return "Unknown"
    
    @property
    def user_id_no(self):
        """Get the user's ID number (Student or Faculty)"""
        if self.user:
            return self.user.id_no
        elif self.student:
            return self.student.id_no
        return "Unknown"
    
    @property
    def user_type(self):
        """Get the user type (Student or Faculty)"""
        if self.user:
            return self.content_type.model.capitalize()
        elif self.student:
            return "Student"
        return "Unknown"