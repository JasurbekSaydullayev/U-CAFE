from rest_framework import permissions


class IsSuperAdminOrOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser or request.user.user_type == "Customer"

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        return obj.user == request.user
