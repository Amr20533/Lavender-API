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


class IsUserOrSpecialist(BasePermission):
    """
    Allows access to authenticated users whose role is either 'user' or 'specialist'.
    """

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        role = getattr(user.profile, 'role', None)
        return role in (RoleChoices.SPECIALIST, RoleChoices.PATIENT)


class IsUser(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        role = getattr(user.profile, 'role', None)
        return role in (RoleChoices.PATIENT)
