from rest_framework.permissions import BasePermission


class IsManager(BasePermission):
    def has_permission(self, request, view):
        if request.user.role != "manager":
            return False
        return True

