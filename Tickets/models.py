from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from Library.models import Student

# Create your models here.
class Ticket(models.Model):
    ISSUE_TYPES = [
        ('pc_issue', 'PC Issue'),
        ('facility_issue', 'Facility Issue'),
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
    
    # Generic foreign key to support both Student and Faculty
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    created_by = GenericForeignKey('content_type', 'object_id')
    
    # Legacy field for backward compatibility - will be deprecated
    issued_by = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True)
    
    issue_type = models.CharField(max_length=20, choices=ISSUE_TYPES)
    status = models.CharField(max_length=20, choices=ISSUE_STATUS, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
    @property
    def creator_name(self):
        """Get the creator's name (Student or Faculty)"""
        if self.created_by:
            return self.created_by.name
        elif self.issued_by:
            return self.issued_by.name
        return "Unknown"
    
    @property
    def creator_id_no(self):
        """Get the creator's ID number (Student or Faculty)"""
        if self.created_by:
            return self.created_by.id_no
        elif self.issued_by:
            return self.issued_by.id_no
        return "Unknown"
    
    @property
    def creator_type(self):
        """Get the creator type (Student or Faculty)"""
        if self.created_by:
            return self.content_type.model.capitalize()
        elif self.issued_by:
            return "Student"
        return "Unknown"