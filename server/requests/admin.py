"""
Admin configuration for requests app.
"""
from django.contrib import admin
from .models import PurchaseRequest, Approval, RequestItem, ReceiptValidation


class RequestItemInline(admin.TabularInline):
    """Inline admin for request items."""
    model = RequestItem
    extra = 1


class ApprovalInline(admin.TabularInline):
    """Inline admin for approvals."""
    model = Approval
    extra = 0
    readonly_fields = ['created_at', 'updated_at']


@admin.register(PurchaseRequest)
class PurchaseRequestAdmin(admin.ModelAdmin):
    """Admin for PurchaseRequest model."""
    list_display = ['title', 'created_by', 'amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['title', 'description', 'created_by__username']
    readonly_fields = ['created_at', 'updated_at', 'purchase_order_file']
    inlines = [RequestItemInline, ApprovalInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'amount', 'status', 'created_by')
        }),
        ('Files', {
            'fields': ('proforma_file', 'purchase_order_file', 'receipt_file')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(Approval)
class ApprovalAdmin(admin.ModelAdmin):
    """Admin for Approval model."""
    list_display = ['request', 'approver', 'level', 'status', 'created_at']
    list_filter = ['status', 'level', 'created_at']
    search_fields = ['request__title', 'approver__username', 'comment']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(RequestItem)
class RequestItemAdmin(admin.ModelAdmin):
    """Admin for RequestItem model."""
    list_display = ['item_name', 'request', 'quantity', 'price', 'total']
    list_filter = ['request']
    search_fields = ['item_name', 'request__title']


@admin.register(ReceiptValidation)
class ReceiptValidationAdmin(admin.ModelAdmin):
    """Admin for ReceiptValidation model."""
    list_display = ['request', 'is_valid', 'discrepancy_amount', 'validated_by', 'validated_at']
    list_filter = ['is_valid', 'validated_at']
    readonly_fields = ['validated_at']

