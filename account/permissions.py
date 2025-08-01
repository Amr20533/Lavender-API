from rest_framework.permissions import BasePermission
from .models import RoleChoices

class IsSpecialist(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.profile.role == RoleChoices.SPECIALIST
