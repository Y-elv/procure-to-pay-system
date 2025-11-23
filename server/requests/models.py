"""
Models for purchase requests and approvals.
"""
from django.db import models
from django.db.models import Q, F
from django.core.exceptions import ValidationError
from core.models import User
import os


def upload_to_proforma(instance, filename):
    """Generate upload path for proforma files."""
    return f'proformas/{instance.id}/{filename}'


def upload_to_po(instance, filename):
    """Generate upload path for purchase order files."""
    return f'purchase_orders/{instance.id}/{filename}'


def upload_to_receipt(instance, filename):
    """Generate upload path for receipt files."""
    return f'receipts/{instance.id}/{filename}'


class PurchaseRequest(models.Model):
    """
    Purchase request model with multi-level approval workflow.
    
    Status flow:
    - PENDING: Initial state, waiting for approvals
    - APPROVED: All approvals completed
    - REJECTED: Any approver rejected
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Relationships
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_requests')
    
    # File uploads
    proforma_file = models.FileField(upload_to=upload_to_proforma, null=True, blank=True)
    purchase_order_file = models.FileField(upload_to=upload_to_po, null=True, blank=True)
    receipt_file = models.FileField(upload_to=upload_to_receipt, null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'purchase_requests'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['created_by', 'status']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.status} ({self.amount})"
    
    def can_be_edited(self):
        """Check if request can be edited (only when pending)."""
        return self.status == 'pending'
    
    def can_be_approved(self):
        """Check if request can be approved (only when pending)."""
        return self.status == 'pending'
    
    def get_approvals(self):
        """Get all approvals for this request."""
        return self.approvals.all().order_by('level', 'created_at')
    
    def get_approval_by_level(self, level):
        """Get approval for a specific level."""
        return self.approvals.filter(level=level).first()
    
    def check_approval_status(self):
        """
        Check approval status and update request status accordingly.
        This is called after each approval action.
        """
        if self.status != 'pending':
            return  # Already finalized
        
        approvals = self.get_approvals()
        
        # Check for rejection
        if approvals.filter(status='rejected').exists():
            self.status = 'rejected'
            self.save(update_fields=['status', 'updated_at'])
            return
        
        # Check if all required approvals are done
        level_1_approval = self.get_approval_by_level(1)
        level_2_approval = self.get_approval_by_level(2)
        
        if level_1_approval and level_2_approval:
            if level_1_approval.status == 'approved' and level_2_approval.status == 'approved':
                self.status = 'approved'
                self.save(update_fields=['status', 'updated_at'])
                # Signal will handle PO generation


class Approval(models.Model):
    """
    Approval model for tracking multi-level approvals.
    Each request requires approvals from level 1 and level 2.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    request = models.ForeignKey(
        PurchaseRequest,
        on_delete=models.CASCADE,
        related_name='approvals'
    )
    approver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='approvals')
    level = models.IntegerField(choices=[(1, 'Level 1'), (2, 'Level 2')])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    comment = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'approvals'
        ordering = ['level', 'created_at']
        unique_together = [['request', 'level']]  # One approval per level per request
        indexes = [
            models.Index(fields=['request', 'level']),
            models.Index(fields=['status', 'level']),
        ]
    
    def __str__(self):
        return f"Approval {self.level} for {self.request.title} - {self.status}"
    
    def clean(self):
        """Validate approval level matches approver role."""
        if self.level == 1 and not self.approver.is_approver_level_1():
            raise ValidationError("Level 1 approval must be done by approver_level_1 user.")
        if self.level == 2 and not self.approver.is_approver_level_2():
            raise ValidationError("Level 2 approval must be done by approver_level_2 user.")
    
    def save(self, *args, **kwargs):
        """Override save to validate and update request status."""
        self.clean()
        super().save(*args, **kwargs)
        # Update request status after approval change
        self.request.check_approval_status()


class RequestItem(models.Model):
    """
    Individual items within a purchase request.
    """
    request = models.ForeignKey(
        PurchaseRequest,
        on_delete=models.CASCADE,
        related_name='items'
    )
    item_name = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'request_items'
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.item_name} x{self.quantity} = {self.total}"
    
    def save(self, *args, **kwargs):
        """Calculate total before saving."""
        self.total = self.quantity * self.price
        super().save(*args, **kwargs)


class ReceiptValidation(models.Model):
    """
    Model to store receipt validation results.
    """
    request = models.OneToOneField(
        PurchaseRequest,
        on_delete=models.CASCADE,
        related_name='receipt_validation'
    )
    is_valid = models.BooleanField(default=False)
    discrepancy_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discrepancy_details = models.JSONField(default=dict, blank=True)
    validated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='validated_receipts')
    validated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'receipt_validations'
    
    def __str__(self):
        return f"Receipt validation for {self.request.title} - {'Valid' if self.is_valid else 'Invalid'}"

