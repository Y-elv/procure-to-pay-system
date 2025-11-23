"""
Views for purchase requests API.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from core.permissions import IsOwnerOrApprover, CanApprove, IsFinance
from .models import PurchaseRequest, Approval, ReceiptValidation
from .serializers import (
    PurchaseRequestSerializer,
    ApprovalActionSerializer,
    ReceiptSubmissionSerializer,
    ReceiptValidationSerializer,
)
from .doc_processing.receipt_validator import validate_receipt_against_po


class PurchaseRequestViewSet(viewsets.ModelViewSet):
    """
    ViewSet for purchase requests.
    
    - Staff can create and view their own requests
    - Approvers can view all requests and approve/reject
    - Finance can view all requests and validate receipts
    """
    serializer_class = PurchaseRequestSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'created_by']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'updated_at', 'amount']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter queryset based on user role."""
        user = self.request.user
        
        if user.is_staff_role():
            # Staff sees only their own requests
            return PurchaseRequest.objects.filter(created_by=user)
        elif user.can_approve() or user.is_finance():
            # Approvers and finance see all requests
            return PurchaseRequest.objects.all()
        else:
            # Fallback
            return PurchaseRequest.objects.filter(created_by=user)
    
    def get_permissions(self):
        """Set permissions based on action."""
        if self.action == 'create':
            # Only staff can create requests
            return [IsAuthenticated()]
        elif self.action in ['approve', 'reject']:
            # Only approvers can approve/reject
            return [IsAuthenticated(), CanApprove()]
        elif self.action == 'submit_receipt':
            # Only request owner can submit receipt
            return [IsAuthenticated()]
        elif self.action == 'validate_receipt':
            # Only finance can validate
            return [IsAuthenticated(), IsFinance()]
        else:
            return [IsAuthenticated(), IsOwnerOrApprover()]
    
    def perform_create(self, serializer):
        """Set created_by to current user."""
        serializer.save(created_by=self.request.user)
        
        # Create initial approval records
        request = serializer.instance
        # In a real system, you'd assign specific approvers based on business logic
        # For now, we'll create approvals when approvers act
    
    @action(detail=True, methods=['patch'])
    def approve(self, request, pk=None):
        """
        Approve a purchase request.
        Creates or updates approval record for the approver's level.
        """
        purchase_request = self.get_object()
        
        if not purchase_request.can_be_approved():
            return Response(
                {'error': 'Request cannot be approved (already finalized).'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = ApprovalActionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        comment = serializer.validated_data.get('comment', '')
        approver = request.user
        
        # Determine approval level based on user role
        if approver.is_approver_level_1():
            level = 1
        elif approver.is_approver_level_2():
            level = 2
        else:
            return Response(
                {'error': 'User does not have approval permissions.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if approval already exists
        approval, created = Approval.objects.get_or_create(
            request=purchase_request,
            level=level,
            defaults={'approver': approver}
        )
        
        # Update approval
        if not created and approval.status != 'pending':
            return Response(
                {'error': f'Level {level} approval already processed.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        approval.status = 'approved'
        approval.comment = comment
        approval.approver = approver
        approval.save()
        
        # Check if request should be auto-approved
        purchase_request.check_approval_status()
        
        serializer = self.get_serializer(purchase_request)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['patch'])
    def reject(self, request, pk=None):
        """
        Reject a purchase request.
        Creates or updates approval record for the approver's level.
        """
        purchase_request = self.get_object()
        
        if not purchase_request.can_be_approved():
            return Response(
                {'error': 'Request cannot be rejected (already finalized).'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = ApprovalActionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        comment = serializer.validated_data.get('comment', '')
        if not comment:
            return Response(
                {'error': 'Rejection comment is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        approver = request.user
        
        # Determine approval level
        if approver.is_approver_level_1():
            level = 1
        elif approver.is_approver_level_2():
            level = 2
        else:
            return Response(
                {'error': 'User does not have approval permissions.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if approval already exists
        approval, created = Approval.objects.get_or_create(
            request=purchase_request,
            level=level,
            defaults={'approver': approver}
        )
        
        # Update approval
        if not created and approval.status != 'pending':
            return Response(
                {'error': f'Level {level} approval already processed.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        approval.status = 'rejected'
        approval.comment = comment
        approval.approver = approver
        approval.save()
        
        # Update request status (will be rejected)
        purchase_request.check_approval_status()
        
        serializer = self.get_serializer(purchase_request)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def submit_receipt(self, request, pk=None):
        """
        Submit receipt file for a purchase request.
        Only the request creator can submit receipts.
        """
        purchase_request = self.get_object()
        
        if purchase_request.created_by != request.user:
            return Response(
                {'error': 'Only request creator can submit receipts.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if purchase_request.status != 'approved':
            return Response(
                {'error': 'Receipt can only be submitted for approved requests.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = ReceiptSubmissionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        purchase_request.receipt_file = serializer.validated_data['receipt_file']
        purchase_request.save(update_fields=['receipt_file'])
        
        serializer = self.get_serializer(purchase_request)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def validate_receipt(self, request, pk=None):
        """
        Validate receipt against purchase order.
        Only finance users can validate receipts.
        """
        purchase_request = self.get_object()
        
        if not purchase_request.receipt_file:
            return Response(
                {'error': 'No receipt file found for this request.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Perform validation
        validation_result = validate_receipt_against_po(purchase_request)
        
        # Create or update validation record
        validation, created = ReceiptValidation.objects.update_or_create(
            request=purchase_request,
            defaults={
                'is_valid': validation_result['is_valid'],
                'discrepancy_amount': validation_result.get('discrepancy_amount'),
                'discrepancy_details': validation_result.get('discrepancy_details', {}),
                'validated_by': request.user,
            }
        )
        
        serializer = ReceiptValidationSerializer(validation)
        return Response(serializer.data, status=status.HTTP_200_OK)

