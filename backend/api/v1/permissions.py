from rest_framework import permissions


class AllReadOnlyPermissions(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class HRAllPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_hr


class HRSafePermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            and request.user.is_authenticated and request.user.is_hr
        )


class EmployeeSafePermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            and request.user.is_authenticated and request.user.is_employee
        )


class EmployeePostPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
            request.method == 'POST'
            and request.user.is_authenticated and request.user.is_employee
        )


class ChiefSafePermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            and request.user.is_authenticated and request.user.is_chief
        )


class ChiefPostPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
            request.method == 'POST'
            and request.user.is_authenticated and request.user.is_chief
        )


class AllowAuthorOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            and request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            and request.user.is_authenticated
            or request.user.is_authenticated and request.user == obj.author
        )
