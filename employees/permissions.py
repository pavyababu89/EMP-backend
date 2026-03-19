from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdmin(BasePermission):
    """Only admin role users can access"""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            hasattr(request.user, 'employee') and
            request.user.employee.role == 'admin'
        )


class IsEmployee(BasePermission):
    """Only employee role users can access"""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            hasattr(request.user, 'employee') and
            request.user.employee.role == 'employee'
        )


class IsAdminOrEmployee(BasePermission):
    """Both admin and employee can access"""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            hasattr(request.user, 'employee')
        )


class IsAdminReadOnlyOrEmployee(BasePermission):
    """
    Admin   → GET only (cannot POST, PUT, PATCH, DELETE)
    Employee → Full access (POST, GET, PUT, PATCH, DELETE own)
    Used for: Attendance, Daily Update
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if not hasattr(request.user, 'employee'):
            return False
        if request.user.employee.role == 'admin':
            return request.method in SAFE_METHODS   # GET only
        return True   # employee has full access