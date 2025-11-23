"""
Core models for user management and authentication.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model with role-based access control.
    
    Roles:
    - staff: Can create purchase requests
    - approver_level_1: Can approve/reject requests (first level)
    - approver_level_2: Can approve/reject requests (second level)
    - finance: Can view all requests and process receipts
    """
    ROLE_CHOICES = [
        ('staff', 'Staff'),
        ('approver_level_1', 'Approver Level 1'),
        ('approver_level_2', 'Approver Level 2'),
        ('finance', 'Finance'),
    ]
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='staff',
        help_text="User's role in the system"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.username} ({self.role})"
    
    def is_staff_role(self):
        """Check if user has staff role."""
        return self.role == 'staff'
    
    def is_approver_level_1(self):
        """Check if user is level 1 approver."""
        return self.role == 'approver_level_1'
    
    def is_approver_level_2(self):
        """Check if user is level 2 approver."""
        return self.role == 'approver_level_2'
    
    def is_finance(self):
        """Check if user is finance role."""
        return self.role == 'finance'
    
    def can_approve(self):
        """Check if user can approve requests."""
        return self.role in ['approver_level_1', 'approver_level_2', 'finance']

