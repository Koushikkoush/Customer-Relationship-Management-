from django.contrib.auth.models import User
from django.db import models

from team.models import Team

class Lead(models.Model):
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'

    CHOICES_PRIORITY = (
        (LOW, 'Low'),
        (MEDIUM, 'Medium'),
        (HIGH, 'High'),
    )

    NEW = 'new'
    CONTACTED = 'contacted'
    WON = 'won'
    PROPOSAL_SENT = 'proposal_sent'
    LOST = 'lost'
    Under_negotiation="under negotiation"

    CHOICES_STATUS = (
        (NEW, 'New'),
        (CONTACTED, 'Contacted'),
        # (WON, 'Won'),
        (PROPOSAL_SENT, 'Proposal Sent'),
        (LOST, 'Lost'),
        (Under_negotiation, 'Under Negotiation'),
    )

    SERVICE_CHOICES = [
        ('Web', 'Web'),
        ('App', 'App'),
        ('Web+App', 'Web + App'),
        ('Other', 'Other')
    ]
    
    team = models.ForeignKey(Team, related_name='leads', on_delete=models.CASCADE)
    client_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    service = models.CharField(max_length=50, choices=SERVICE_CHOICES, default='Web')
    custom_service = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    priority = models.CharField(max_length=20, choices=CHOICES_PRIORITY, default=MEDIUM)
    status = models.CharField(max_length=20, choices=CHOICES_STATUS, default=NEW)
    converted_to_client = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='leads', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    
    def soft_delete(self):
        self.is_deleted = True
        self.save()

    class Meta:
        ordering = ('created_at',)

    def __str__(self):
        return f"Lead for {self.client_name if self.client_name else self.email}"

class LeadFile(models.Model):
    team = models.ForeignKey(Team, related_name='lead_files', on_delete=models.CASCADE)
    lead = models.ForeignKey(Lead, related_name='files', on_delete=models.CASCADE)
    file = models.FileField(upload_to='leadfiles')
    created_by = models.ForeignKey(User, related_name='lead_files', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.created_by.username

class Comment(models.Model):
    team = models.ForeignKey(Team, related_name='lead_comments', on_delete=models.CASCADE)
    lead = models.ForeignKey(Lead, related_name='comments', on_delete=models.CASCADE)
    content = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, related_name='lead_comments', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.created_by.username


class Activity(models.Model):
    ACTIVITY_CHOICES = [
        ('call', 'Call'),
        ('meeting', 'Meeting'),
        ('email', 'Email'),
    ]

    lead = models.ForeignKey(Lead, related_name='activities', on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=10, choices=ACTIVITY_CHOICES)
    title = models.CharField(max_length=255)
    date = models.DateField()
    time = models.TimeField()
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-time']
        verbose_name_plural = 'Activities'

    def __str__(self):
        return f"{self.get_activity_type_display()} with {self.lead.client_name}"