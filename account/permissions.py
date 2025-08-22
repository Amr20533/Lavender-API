from rest_framework.permissions import BasePermission
from .models import RoleChoices

# class IsSpecialist(BasePermission):
#     def has_permission(self, request, view):
#         return request.user.is_authenticated and request.user.profile.role == RoleChoices.SPECIALIST


class IsSpecialist(BasePermission):
    """
    Allows access only to authenticated users with the 'specialist' role.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            hasattr(request.user, "profile") and 
            request.user.profile.role == RoleChoices.SPECIALIST
        )
