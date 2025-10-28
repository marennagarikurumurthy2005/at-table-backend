from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Allow admin users to edit, others can only read.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class IsAdmin(permissions.BasePermission):
    """
    Allow only admin users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_staff
