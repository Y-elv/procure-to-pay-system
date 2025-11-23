"""
Custom permissions for role-based access control.
"""
from rest_framework import permissions


class IsStaff(permissions.BasePermission):
    """Permission for staff users."""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_staff_role()


class IsApproverLevel1(permissions.BasePermission):
    """Permission for level 1 approvers."""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_approver_level_1()


class IsApproverLevel2(permissions.BasePermission):
    """Permission for level 2 approvers."""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_approver_level_2()


class IsFinance(permissions.BasePermission):
    """Permission for finance users."""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_finance()


class CanApprove(permissions.BasePermission):
    """Permission for users who can approve requests."""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.can_approve()


class IsOwnerOrApprover(permissions.BasePermission):
    """
    Permission that allows:
    - Owner (creator) to view/edit their own requests
    - Approvers to view all requests
    - Finance to view all requests
    """
    
    def has_object_permission(self, request, view, obj):
        # Owner can always access
        if obj.created_by == request.user:
            return True
        
        # Approvers and finance can view
        if request.user.can_approve() or request.user.is_finance():
            return True
        
        return False

