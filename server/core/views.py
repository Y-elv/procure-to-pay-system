"""
Views for authentication and user management.
"""
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import RegisterSerializer, LoginSerializer, TokenSerializer, UserSerializer
from .models import User


@swagger_auto_schema(
    method='post',
    operation_summary="Register new user",
    operation_description="""
    Register a new user account in the system.
    
    **Roles available:**
    - `staff`: Can create purchase requests
    - `approver_level_1`: First-level approver
    - `approver_level_2`: Second-level approver
    - `finance`: Can validate receipts
    
    Returns JWT access and refresh tokens upon successful registration.
    """,
    responses={
        201: openapi.Response(
            'User created successfully',
            TokenSerializer,
            examples={
                "application/json": {
                    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                    "user": {
                        "id": 1,
                        "username": "john_doe",
                        "email": "john@example.com",
                        "role": "staff",
                        "first_name": "John",
                        "last_name": "Doe",
                        "date_joined": "2025-01-15T10:30:00Z"
                    }
                }
            }
        ),
        400: openapi.Response('Bad request - validation errors', examples={
            "application/json": {
                "username": ["This field is required."],
                "password": ["This field is required."]
            }
        })
    },
    tags=['Authentication'],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "username": openapi.Schema(type=openapi.TYPE_STRING, description="Username"),
            "email": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL, description="Email address"),
            "password": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_PASSWORD, description="Password (min 8 characters)"),
            "password_confirm": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_PASSWORD, description="Password confirmation"),
            "role": openapi.Schema(type=openapi.TYPE_STRING, enum=["staff", "approver_level_1", "approver_level_2", "finance"], description="User role"),
            "first_name": openapi.Schema(type=openapi.TYPE_STRING, description="First name"),
            "last_name": openapi.Schema(type=openapi.TYPE_STRING, description="Last name"),
        },
        required=["username", "email", "password", "password_confirm"],
        example={
            "username": "john_doe",
            "email": "john@example.com",
            "password": "securepass123",
            "password_confirm": "securepass123",
            "role": "staff",
            "first_name": "John",
            "last_name": "Doe"
        }
    )
)
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """Register a new user."""
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='post',
    operation_summary="User login",
    operation_description="""
    Authenticate user and receive JWT access and refresh tokens.
    
    Use the `access` token in the Authorization header for authenticated requests:
    ```
    Authorization: Bearer {access_token}
    ```
    
    Use the `refresh` token to obtain a new access token when it expires.
    """,
    responses={
        200: openapi.Response(
            'Login successful',
            TokenSerializer,
            examples={
                "application/json": {
                    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                    "user": {
                        "id": 1,
                        "username": "john_doe",
                        "email": "john@example.com",
                        "role": "staff",
                        "first_name": "John",
                        "last_name": "Doe",
                        "date_joined": "2025-01-15T10:30:00Z"
                    }
                }
            }
        ),
        400: openapi.Response('Bad request - invalid credentials', examples={
            "application/json": {
                "non_field_errors": ["Invalid credentials."]
            }
        })
    },
    tags=['Authentication'],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "username": openapi.Schema(type=openapi.TYPE_STRING, description="Username"),
            "password": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_PASSWORD, description="Password"),
        },
        required=["username", "password"],
        example={
            "username": "john_doe",
            "password": "securepass123"
        }
    )
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """Login and get JWT tokens."""
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='post',
    operation_description="Logout and blacklist refresh token",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='Refresh token to blacklist')
        },
        required=['refresh']
    ),
    responses={
        200: openapi.Response('Logout successful', openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={'message': openapi.Schema(type=openapi.TYPE_STRING)}
        )),
        400: 'Bad request'
    },
    tags=['Authentication'],
    security=[{'Bearer': []}]
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """Logout and blacklist refresh token."""
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        return Response({'message': 'Successfully logged out.'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='get',
    operation_summary="Get current user",
    operation_description="Get information about the currently authenticated user.",
    manual_parameters=[
        openapi.Parameter(
            'Authorization',
            openapi.IN_HEADER,
            description="JWT token in format: Bearer {token}",
            type=openapi.TYPE_STRING,
            required=True
        )
    ],
    responses={
        200: openapi.Response(
            'User information',
            UserSerializer,
            examples={
                "application/json": {
                    "id": 1,
                    "username": "john_doe",
                    "email": "john@example.com",
                    "role": "staff",
                    "first_name": "John",
                    "last_name": "Doe",
                    "date_joined": "2025-01-15T10:30:00Z"
                }
            }
        ),
        401: openapi.Response('Unauthorized', examples={
            "application/json": {
                "detail": "Authentication credentials were not provided."
            }
        })
    },
    tags=['Authentication'],
    security=[{'Bearer': []}]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    """Get current user information."""
    serializer = UserSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)


class UserListView(generics.ListAPIView):
    """
    List all users (for admin/approvers).
    
    GET /api/auth/users/
    - Returns list of all users
    - Requires authentication
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_summary="List all users",
        operation_description="List all users in the system. Available to authenticated users.",
        responses={
            200: openapi.Response(
                'List of users',
                UserSerializer(many=True),
                examples={
                    "application/json": [
                        {
                            "id": 1,
                            "username": "john_doe",
                            "email": "john@example.com",
                            "role": "staff",
                            "first_name": "John",
                            "last_name": "Doe",
                            "date_joined": "2025-01-15T10:30:00Z"
                        }
                    ]
                }
            ),
            401: 'Unauthorized'
        },
        tags=['Users'],
        security=[{'Bearer': []}]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

