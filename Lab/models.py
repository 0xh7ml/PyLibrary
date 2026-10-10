from django.db import models
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from Library.models import Student, Faculty, Department


class LabSeat(models.Model):
    PC_STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Reserved', 'Reserved'),
        ('Maintenance', 'Maintenance'),
    ]
    pc_no = models.CharField(max_length=50)
    layout_slot = models.PositiveIntegerField(null=True, blank=True, unique=True)
    status = models.CharField(max_length=50, choices=PC_STATUS_CHOICES, default='Available')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    notes = models.CharField(max_length=255, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Lab Seat"
        verbose_name_plural = "Lab Seats"
        db_table = "tb_lab_seats"
        ordering = ['layout_slot', 'pc_no']

    def __str__(self):
        return f"{self.pc_no}"


class LabSession(models.Model):
    """Track Computer Lab PC usage sessions"""
    SESSION_STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Exited', 'Exited'),
    ]

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    user = GenericForeignKey('content_type', 'object_id')

    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True)
    seat = models.ForeignKey(LabSeat, on_delete=models.CASCADE, related_name='sessions')
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=SESSION_STATUS_CHOICES, default='Active')
    purpose = models.CharField(max_length=255, blank=True, default='Lab Practice')

    class Meta:
        verbose_name = "Lab Session"
        verbose_name_plural = "Lab Sessions"
        db_table = "tb_lab_sessions"
        ordering = ['-start_time']

    def __str__(self):
        user_name = self.user.name if self.user else (self.student.name if self.student else "Unknown")
        return f"{user_name} - {self.seat.pc_no} - {self.start_time.strftime('%Y-%m-%d %H:%M')}"

    def end_session(self):
        """End the lab session and free up the seat"""
        self.end_time = timezone.now()
        self.status = 'Exited'
        self.seat.status = 'Available'
        self.seat.save()
        self.save()

    @property
    def duration(self):
        """Calculate duration spent in lab"""
        if self.end_time:
            return self.end_time - self.start_time
        return None

    @property
    def duration_display(self):
        """Get formatted duration string for display"""
        if self.end_time:
            duration = self.end_time - self.start_time
            return str(duration).split('.')[0]
        return 'Active'

    @property
    def formatted_start_time(self):
        return self.start_time.strftime('%Y-%m-%d %H:%M:%S')

    @property
    def formatted_end_time(self):
        return self.end_time.strftime('%Y-%m-%d %H:%M:%S') if self.end_time else 'Active'

    @property
    def user_name(self):
        if self.user:
            return self.user.name
        elif self.student:
            return self.student.name
        return "Unknown"

    @property
    def user_id_no(self):
        if self.user:
            return self.user.id_no
        elif self.student:
            return self.student.id_no
        return "Unknown"

    @property
    def user_type(self):
        if self.user:
            return self.content_type.model.capitalize()
        elif self.student:
            return "Student"
        return "Unknown"

    @property
    def user_department_name(self):
        if self.user and getattr(self.user, 'department', None):
            return self.user.department.name
        if self.student and self.student.department:
            return self.student.department.name
        return "N/A"


class LabTicket(models.Model):
    """Tickets reported for Lab PCs or general lab facilities"""
    ISSUE_TYPES = [
        ('pc_issue', 'PC Hardware Issue'),
        ('software_issue', 'Software / OS Issue'),
        ('network_issue', 'Network / Internet Issue'),
        ('facility_issue', 'Lab Facility Issue'),
        ('other_issue', 'Other Issue'),
    ]

    ISSUE_STATUS = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    issue_type = models.CharField(max_length=30, choices=ISSUE_TYPES, default='pc_issue')
    seat = models.ForeignKey(LabSeat, on_delete=models.SET_NULL, null=True, blank=True, related_name='tickets')

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    created_by = GenericForeignKey('content_type', 'object_id')

    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True)

    status = models.CharField(max_length=20, choices=ISSUE_STATUS, default='open')
    admin_notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Lab Ticket"
        verbose_name_plural = "Lab Tickets"
        db_table = "tb_lab_tickets"
        ordering = ['-created_at']

    def __str__(self):
        return f"Lab #{self.id}: {self.title}"

    @property
    def creator_name(self):
        if self.created_by:
            return self.created_by.name
        elif self.student:
            return self.student.name
        return "Unknown"

    @property
    def creator_id_no(self):
        if self.created_by:
            return self.created_by.id_no
        elif self.student:
            return self.student.id_no
        return "Unknown"

    @property
    def creator_type(self):
        if self.created_by:
            return self.content_type.model.capitalize()
        elif self.student:
            return "Student"
        return "Unknown"
