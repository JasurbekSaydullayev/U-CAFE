from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_superuser


class IsAdminOrOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser or request.user

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        return request.user == obj.user


class IsManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == "Manager" or request.user.is_superuser


class IsSeller(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated and
                (request.user.user_type == "Seller" or request.user.is_superuser
                 or request.user.user_type == 'Manager'))


class IsCook(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == "Cook" or request.user.is_superuser


class IsSellerOrCook(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
                request.user.user_type == "Seller" or request.user.user_type == 'Cook') or request.user.is_superuser


class IsAdminOrManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.user_type == 'Manager' or request.user.is_superuser


class IsManagerOrOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser or request.user.user_type == "Manager":
            return True
        return request.user == obj
