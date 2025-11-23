"""
Serializers for purchase requests app.
"""
from rest_framework import serializers
from django.db import transaction
from core.models import User
from .models import PurchaseRequest, Approval, RequestItem, ReceiptValidation


class RequestItemSerializer(serializers.ModelSerializer):
    """Serializer for request items."""
    
    class Meta:
        model = RequestItem
        fields = ['id', 'item_name', 'quantity', 'price', 'total']
        read_only_fields = ['id', 'total']


class ApprovalSerializer(serializers.ModelSerializer):
    """Serializer for approvals."""
    approver_username = serializers.CharField(source='approver.username', read_only=True)
    approver_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Approval
        fields = ['id', 'approver', 'approver_username', 'approver_name', 'level', 'status', 'comment', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_approver_name(self, obj):
        """Get approver's full name."""
        return obj.approver.get_full_name() or obj.approver.username


class PurchaseRequestSerializer(serializers.ModelSerializer):
    """Serializer for purchase requests."""
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    created_by_name = serializers.SerializerMethodField()
    items = RequestItemSerializer(many=True, required=False)
    approvals = ApprovalSerializer(many=True, read_only=True)
    can_edit = serializers.BooleanField(read_only=True)
    can_approve = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = PurchaseRequest
        fields = [
            'id', 'title', 'description', 'amount', 'status',
            'created_by', 'created_by_username', 'created_by_name',
            'proforma_file', 'purchase_order_file', 'receipt_file',
            'items', 'approvals',
            'created_at', 'updated_at',
            'can_edit', 'can_approve',
        ]
        read_only_fields = ['id', 'created_by', 'status', 'purchase_order_file', 'created_at', 'updated_at']
    
    def get_created_by_name(self, obj):
        """Get creator's full name."""
        return obj.created_by.get_full_name() or obj.created_by.username
    
    def create(self, validated_data):
        """Create purchase request with items."""
        items_data = validated_data.pop('items', [])
        request = PurchaseRequest.objects.create(**validated_data)
        
        # Create items
        for item_data in items_data:
            RequestItem.objects.create(request=request, **item_data)
        
        # Create initial approval records for both levels
        # These will be pending until approvers act
        # Note: In real system, you'd assign specific approvers
        # For now, we create placeholder approvals
        
        return request
    
    def update(self, instance, validated_data):
        """Update purchase request (only if pending)."""
        if not instance.can_be_edited():
            raise serializers.ValidationError("Cannot edit request that is not pending.")
        
        items_data = validated_data.pop('items', None)
        
        # Update request fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update items if provided
        if items_data is not None:
            # Delete existing items
            instance.items.all().delete()
            # Create new items
            for item_data in items_data:
                RequestItem.objects.create(request=instance, **item_data)
        
        return instance


class ApprovalActionSerializer(serializers.Serializer):
    """Serializer for approve/reject actions."""
    comment = serializers.CharField(required=False, allow_blank=True)
    level = serializers.IntegerField(required=False)  # Auto-determined if not provided


class ReceiptSubmissionSerializer(serializers.Serializer):
    """Serializer for receipt submission."""
    receipt_file = serializers.FileField()


class ReceiptValidationSerializer(serializers.ModelSerializer):
    """Serializer for receipt validation results."""
    validated_by_username = serializers.CharField(source='validated_by.username', read_only=True)
    
    class Meta:
        model = ReceiptValidation
        fields = [
            'id', 'is_valid', 'discrepancy_amount', 'discrepancy_details',
            'validated_by', 'validated_by_username', 'validated_at'
        ]
        read_only_fields = ['id', 'validated_by', 'validated_at']

