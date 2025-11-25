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
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
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
    
    @swagger_auto_schema(
        operation_summary="List purchase requests",
        operation_description="""
        List purchase requests with filtering, searching, and pagination.
        
        **Role-based filtering:**
        - Staff: Only their own requests
        - Approvers/Finance: All requests
        
        **Query Parameters:**
        - `status`: Filter by status (pending, approved, rejected)
        - `created_by`: Filter by creator user ID
        - `search`: Search in title and description
        - `ordering`: Order by field (-created_at, amount, etc.)
        - `page`: Page number for pagination
        """,
        manual_parameters=[
            openapi.Parameter(
                'status',
                openapi.IN_QUERY,
                description="Filter by request status",
                type=openapi.TYPE_STRING,
                enum=['pending', 'approved', 'rejected']
            ),
            openapi.Parameter(
                'created_by',
                openapi.IN_QUERY,
                description="Filter by creator user ID",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'search',
                openapi.IN_QUERY,
                description="Search in title and description",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'ordering',
                openapi.IN_QUERY,
                description="Order by field (prefix with - for descending)",
                type=openapi.TYPE_STRING,
                enum=['created_at', '-created_at', 'updated_at', '-updated_at', 'amount', '-amount']
            ),
            openapi.Parameter(
                'page',
                openapi.IN_QUERY,
                description="Page number",
                type=openapi.TYPE_INTEGER
            )
        ],
        responses={
            200: openapi.Response(
                'Paginated list of purchase requests',
                PurchaseRequestSerializer(many=True)
            ),
            401: 'Unauthorized'
        },
        tags=['Purchase Requests'],
        security=[{'Bearer': []}]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Create purchase request",
        operation_description="""
        Create a new purchase request. Only staff users can create requests.
        
        **Required fields:**
        - title: Request title
        - description: Request description
        - amount: Total amount
        
        **Optional fields:**
        - items: List of request items
        - proforma_file: Proforma invoice file
        """,
        responses={
            201: openapi.Response(
                'Request created successfully',
                PurchaseRequestSerializer,
                examples={
                    "application/json": {
                        "id": 1,
                        "title": "Office Supplies Q1",
                        "description": "Purchase office supplies for first quarter",
                        "amount": "1500.00",
                        "status": "pending",
                        "created_by": 1,
                        "created_by_username": "john_doe",
                        "items": [],
                        "approvals": [],
                        "can_edit": True,
                        "can_approve": True,
                        "created_at": "2025-01-15T10:30:00Z"
                    }
                }
            ),
            400: 'Bad request - validation errors',
            401: 'Unauthorized'
        },
        tags=['Purchase Requests'],
        security=[{'Bearer': []}],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "title": openapi.Schema(type=openapi.TYPE_STRING, description="Request title"),
                "description": openapi.Schema(type=openapi.TYPE_STRING, description="Request description"),
                "amount": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DECIMAL, description="Total amount"),
                "items": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "item_name": openapi.Schema(type=openapi.TYPE_STRING, description="Item name"),
                            "quantity": openapi.Schema(type=openapi.TYPE_INTEGER, description="Quantity"),
                            "price": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DECIMAL, description="Price per unit"),
                        },
                        required=["item_name", "quantity", "price"]
                    ),
                    description="List of request items"
                ),
                "proforma_file": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_BINARY, description="Proforma invoice file"),
            },
            required=["title", "description", "amount"],
            example={
                "title": "Office Supplies Q1",
                "description": "Purchase office supplies for first quarter",
                "amount": "1500.00",
                "items": [
                    {
                        "item_name": "Printer Paper",
                        "quantity": 10,
                        "price": "25.00"
                    },
                    {
                        "item_name": "Pens",
                        "quantity": 50,
                        "price": "2.00"
                    }
                ]
            }
        )
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Get purchase request detail",
        operation_description="Get detailed information about a specific purchase request.",
        responses={
            200: openapi.Response('Purchase request details', PurchaseRequestSerializer),
            404: 'Not found',
            401: 'Unauthorized'
        },
        tags=['Purchase Requests'],
        security=[{'Bearer': []}]
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Update purchase request",
        operation_description="""
        Update a purchase request. Only pending requests can be updated.
        Only the request creator can update their own requests.
        """,
        request_body=PurchaseRequestSerializer,
        responses={
            200: openapi.Response('Request updated successfully', PurchaseRequestSerializer),
            400: 'Bad request - cannot edit non-pending request',
            403: 'Forbidden - not the request owner',
            404: 'Not found'
        },
        tags=['Purchase Requests'],
        security=[{'Bearer': []}]
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Partial update purchase request",
        operation_description="Partially update a purchase request (PATCH). Same rules as PUT.",
        request_body=PurchaseRequestSerializer,
        responses={
            200: openapi.Response('Request updated successfully', PurchaseRequestSerializer),
            400: 'Bad request',
            403: 'Forbidden',
            404: 'Not found'
        },
        tags=['Purchase Requests'],
        security=[{'Bearer': []}]
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Delete purchase request",
        operation_description="Delete a purchase request. Only pending requests can be deleted.",
        responses={
            204: 'No content - request deleted',
            400: 'Bad request - cannot delete non-pending request',
            403: 'Forbidden',
            404: 'Not found'
        },
        tags=['Purchase Requests'],
        security=[{'Bearer': []}]
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
    def get_queryset(self):
        """Filter queryset based on user role."""
        # Handle schema generation (Swagger UI) - avoid AnonymousUser errors
        if getattr(self, 'swagger_fake_view', False):
            return PurchaseRequest.objects.none()
        
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
    
    @swagger_auto_schema(
        operation_summary="Approve purchase request",
        operation_description="""
        Approve a purchase request. Creates or updates approval record for the approver's level.
        
        **Approval Levels:**
        - Level 1 approvers approve first
        - Level 2 approvers approve second
        - Request becomes approved when both levels approve
        
        **Required roles:** approver_level_1 or approver_level_2
        """,
        responses={
            200: openapi.Response(
                'Request approved successfully',
                PurchaseRequestSerializer,
                examples={
                    "application/json": {
                        "id": 1,
                        "title": "Office Supplies",
                        "status": "pending",
                        "approvals": [
                            {
                                "id": 1,
                                "level": 1,
                                "status": "approved",
                                "comment": "Approved - within budget",
                                "approver_username": "approver1"
                            }
                        ]
                    }
                }
            ),
            400: openapi.Response('Bad request', examples={
                "application/json": {
                    "error": "Request cannot be approved (already finalized)."
                }
            }),
            403: 'Forbidden - user does not have approval permissions'
        },
        tags=['Purchase Requests'],
        security=[{'Bearer': []}],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "comment": openapi.Schema(type=openapi.TYPE_STRING, description="Approval comment (optional)"),
                "level": openapi.Schema(type=openapi.TYPE_INTEGER, description="Approval level (auto-determined if not provided)", enum=[1, 2]),
            },
            example={
                "comment": "Approved - within budget limits"
            }
        )
    )
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
    
    @swagger_auto_schema(
        operation_summary="Reject purchase request",
        operation_description="""
        Reject a purchase request. Creates or updates approval record for the approver's level.
        
        **Important:** Comment is required for rejection.
        
        **Required roles:** approver_level_1 or approver_level_2
        """,
        responses={
            200: openapi.Response(
                'Request rejected successfully',
                PurchaseRequestSerializer,
                examples={
                    "application/json": {
                        "id": 1,
                        "title": "Office Supplies",
                        "status": "rejected",
                        "approvals": [
                            {
                                "id": 1,
                                "level": 1,
                                "status": "rejected",
                                "comment": "Rejected - exceeds budget",
                                "approver_username": "approver1"
                            }
                        ]
                    }
                }
            ),
            400: openapi.Response('Bad request', examples={
                "application/json": {
                    "error": "Rejection comment is required."
                }
            }),
            403: 'Forbidden - user does not have approval permissions'
        },
        tags=['Purchase Requests'],
        security=[{'Bearer': []}],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "comment": openapi.Schema(type=openapi.TYPE_STRING, description="Rejection comment (required)"),
                "level": openapi.Schema(type=openapi.TYPE_INTEGER, description="Approval level (auto-determined if not provided)", enum=[1, 2]),
            },
            required=["comment"],
            example={
                "comment": "Rejected - exceeds budget limit"
            }
        )
    )
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
    
    @swagger_auto_schema(
        operation_summary="Submit receipt",
        operation_description="""
        Submit receipt file for an approved purchase request.
        
        **Requirements:**
        - Request must be in 'approved' status
        - Only the request creator can submit receipts
        - Receipt file must be uploaded (PDF, image, etc.)
        """,
        request_body=ReceiptSubmissionSerializer,
        responses={
            200: openapi.Response(
                'Receipt submitted successfully',
                PurchaseRequestSerializer,
                examples={
                    "application/json": {
                        "id": 1,
                        "title": "Office Supplies",
                        "status": "approved",
                        "receipt_file": "/media/receipts/1/receipt.pdf"
                    }
                }
            ),
            400: openapi.Response('Bad request', examples={
                "application/json": {
                    "error": "Receipt can only be submitted for approved requests."
                }
            }),
            403: 'Forbidden - only request creator can submit receipts'
        },
        tags=['Purchase Requests'],
        security=[{'Bearer': []}]
    )
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
    
    @swagger_auto_schema(
        operation_summary="Validate receipt",
        operation_description="""
        Validate receipt against purchase order. Compares receipt amounts and items with the PO.
        
        **Required role:** finance
        
        **Validation checks:**
        - Amount matches PO
        - Items match PO
        - No discrepancies
        """,
        responses={
            200: openapi.Response(
                'Receipt validation result',
                ReceiptValidationSerializer,
                examples={
                    "application/json": {
                        "id": 1,
                        "is_valid": True,
                        "discrepancy_amount": None,
                        "discrepancy_details": {},
                        "validated_by": 3,
                        "validated_by_username": "finance_user",
                        "validated_at": "2025-01-15T12:00:00Z"
                    }
                }
            ),
            400: openapi.Response('Bad request', examples={
                "application/json": {
                    "error": "No receipt file found for this request."
                }
            }),
            403: 'Forbidden - only finance can validate receipts'
        },
        tags=['Purchase Requests'],
        security=[{'Bearer': []}]
    )
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
    
    @swagger_auto_schema(
        operation_summary="List reviewed requests",
        operation_description="""
        List reviewed requests (approved or rejected). Available to approvers and finance.
        
        **Query Parameters:**
        - `my_reviews=true`: Filter to show only requests reviewed by current user
        - `status`: Filter by status (approved, rejected)
        - `search`: Search in title and description
        - `ordering`: Order by field
        - `page`: Page number
        """,
        manual_parameters=[
            openapi.Parameter(
                'my_reviews',
                openapi.IN_QUERY,
                description="Filter to show only requests reviewed by current user",
                type=openapi.TYPE_BOOLEAN
            ),
            openapi.Parameter(
                'status',
                openapi.IN_QUERY,
                description="Filter by status",
                type=openapi.TYPE_STRING,
                enum=['approved', 'rejected']
            ),
            openapi.Parameter(
                'search',
                openapi.IN_QUERY,
                description="Search in title and description",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'ordering',
                openapi.IN_QUERY,
                description="Order by field",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'page',
                openapi.IN_QUERY,
                description="Page number",
                type=openapi.TYPE_INTEGER
            )
        ],
        responses={
            200: openapi.Response('List of reviewed requests', PurchaseRequestSerializer(many=True)),
            401: 'Unauthorized',
            403: 'Forbidden - only approvers and finance can view reviewed requests'
        },
        tags=['Purchase Requests'],
        security=[{'Bearer': []}]
    )
    @action(detail=False, methods=['get'])
    def reviewed(self, request):
        """
        List reviewed requests (approved or rejected).
        Available to approvers to view requests they have reviewed.
        """
        user = request.user
        
        if not (user.can_approve() or user.is_finance()):
            return Response(
                {'error': 'Only approvers and finance can view reviewed requests.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get requests that have been reviewed (approved or rejected)
        queryset = PurchaseRequest.objects.filter(
            Q(status='approved') | Q(status='rejected')
        )
        
        # Filter by approver if they want to see only their reviewed requests
        approver_filter = request.query_params.get('my_reviews', None)
        if approver_filter == 'true':
            # Get requests where this user has made an approval
            approval_request_ids = Approval.objects.filter(
                approver=user
            ).values_list('request_id', flat=True)
            queryset = queryset.filter(id__in=approval_request_ids)
        
        # Apply filters, search, and ordering
        queryset = self.filter_queryset(queryset)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        operation_summary="List pending requests",
        operation_description="""
        List pending requests awaiting approval. Available to approvers and finance.
        
        **Query Parameters:**
        - `created_by`: Filter by creator user ID
        - `search`: Search in title and description
        - `ordering`: Order by field
        - `page`: Page number
        """,
        manual_parameters=[
            openapi.Parameter(
                'created_by',
                openapi.IN_QUERY,
                description="Filter by creator user ID",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'search',
                openapi.IN_QUERY,
                description="Search in title and description",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'ordering',
                openapi.IN_QUERY,
                description="Order by field",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'page',
                openapi.IN_QUERY,
                description="Page number",
                type=openapi.TYPE_INTEGER
            )
        ],
        responses={
            200: openapi.Response('List of pending requests', PurchaseRequestSerializer(many=True)),
            401: 'Unauthorized',
            403: 'Forbidden - only approvers and finance can view pending requests'
        },
        tags=['Purchase Requests'],
        security=[{'Bearer': []}]
    )
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """
        List pending requests awaiting approval.
        Available to approvers to view requests that need their review.
        """
        user = request.user
        
        if not (user.can_approve() or user.is_finance()):
            return Response(
                {'error': 'Only approvers and finance can view pending requests.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get pending requests
        queryset = PurchaseRequest.objects.filter(status='pending')
        
        # Apply filters, search, and ordering
        queryset = self.filter_queryset(queryset)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

