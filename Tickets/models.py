from django.db import models
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
    issued_by = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True)
    issue_type = models.CharField(max_length=20, choices=ISSUE_TYPES)
    status = models.CharField(max_length=20, choices=ISSUE_STATUS, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title