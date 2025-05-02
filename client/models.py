from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

from team.models import Team

class Client(models.Model):
    SERVICE_CHOICES = [
        ('Web', 'Web'),
        ('App', 'App'),
        ('Web+App', 'Web + App'),
        ('Other', 'Other')  # Allows manual text input
    ]

    team = models.ForeignKey(Team, related_name='clients', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    service = models.CharField(max_length=50, choices=SERVICE_CHOICES, default='Web')
    custom_service = models.CharField(max_length=255, blank=True, null=True) 
    contacted_person_name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    
    # Project cost fields
    min_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    max_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    approved_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    gst_service_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    final_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    # Project timeline fields
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    working_days = models.IntegerField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    
    def soft_delete(self):
        self.is_deleted = True
        self.save()
    
    created_by = models.ForeignKey(User, related_name='clients', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # Handle cost range if provided
        if hasattr(self, 'cost_range') and self.cost_range:
            try:
                min_cost, max_cost = map(float, self.cost_range.split('-'))
                self.min_cost = min_cost
                self.max_cost = max_cost
            except (ValueError, AttributeError):
                pass
    
        # Calculate final cost
        if self.approved_cost is not None and self.gst_service_percentage is not None:
            try:
                gst_amount = float(self.approved_cost) * (float(self.gst_service_percentage) / 100)
                self.final_cost = float(self.approved_cost) + gst_amount
            except (ValueError, TypeError):
                pass
    
        # Calculate end date based on working days
        if self.start_date and self.working_days:
            try:
                current_date = self.start_date
                remaining_days = int(self.working_days)
                
                if remaining_days > 0:
                    while remaining_days > 0:
                        current_date += timedelta(days=1)
                        # Skip weekends (0 = Sunday, 6 = Saturday)
                        if current_date.weekday() < 5:  # Monday = 0, Friday = 4
                            remaining_days -= 1
                    self.end_date = current_date
            except (ValueError, TypeError):
                pass
        
        super().save(*args, **kwargs)
    
    @property
    def cost_range_display(self):
        if self.min_cost and self.max_cost:
            return f"${self.min_cost:,.2f} - ${self.max_cost:,.2f}"
        elif self.min_cost:
            return f"${self.min_cost:,.2f}"
        return "Not specified"


class Comment(models.Model):
    team = models.ForeignKey(Team, related_name='client_comments', on_delete=models.CASCADE)
    client = models.ForeignKey(Client, related_name='comments', on_delete=models.CASCADE)
    content = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, related_name='client_comments', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.created_by.username

class ClientFile(models.Model):
    team = models.ForeignKey(Team, related_name='client_files', on_delete=models.CASCADE)
    client = models.ForeignKey(Client, related_name='files', on_delete=models.CASCADE)
    file = models.FileField(upload_to='clientfiles')
    comment = models.TextField(blank=True, null=True)  # Add this field
    created_by = models.ForeignKey(User, related_name='client_files', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.file.name} - {self.created_by.username}"