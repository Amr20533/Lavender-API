from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password
from rest_framework.permissions import BasePermission
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from rest_framework.exceptions import PermissionDenied
from .serializers import *
from .models import RoleChoices
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from datetime import timedelta

@api_view(['POST'])
def register_user(request):
    data = request.data
    serializer = CreateAccountSerializer(data=data)

    try:
        if serializer.is_valid():
            email = data.get('email')

            if not User.objects.filter(email=email).exists():
                user = User.objects.create(
                    first_name=data.get('first_name'),
                    last_name=data.get('last_name'),
                    username=email,
                    email=email,
                    password=make_password(data.get('password'))
                )
                user.profile.role = RoleChoices.PATIENT  # 👈 default role
                user.profile.save()

                return Response({
                    "status": "success",
                    "message": f"Successfully created your {user.profile.role} account!",
                }, status=status.HTTP_201_CREATED)

            return Response({
                "status": "failed",
                "message": "An account with this email already exists.",
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "status": "failed",
            "message": serializer.errors,
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as error:
        return Response({
            "status": "failed",
            "message": f"Error while creating account: {error}",
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def login_user(request):
    serializer = LoginSerializer(data=request.data)

    if serializer.is_valid():
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({
                "status": "failed",
                "message": "Invalid email or password"
            }, status=status.HTTP_401_UNAUTHORIZED)

        user = authenticate(request, username=user.username, password=password)

        if user is not None and user.profile.role == RoleChoices.PATIENT:
            login(request, user)
            refresh = RefreshToken.for_user(user)
            return Response({
                "status": "success",
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            }, status=status.HTTP_200_OK)

        return Response({
            "status": "failed",
            "message": "Invalid credentials or user is not a regular user.",
        }, status=status.HTTP_401_UNAUTHORIZED)

    return Response({
        "status": "failed",
        "message": serializer.errors,
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def login_specialist(request):
    serializer = LoginSerializer(data=request.data)

    if serializer.is_valid():
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({
                "status": "failed",
                "message": "Invalid email or password"
            }, status=status.HTTP_401_UNAUTHORIZED)

        user = authenticate(request, username=user.username, password=password)

        if user is not None and user.profile.role == RoleChoices.SPECIALIST:
            login(request, user)
            refresh = RefreshToken.for_user(user)
            return Response({
                "status": "success",
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            }, status=status.HTTP_200_OK)

        return Response({
            "status": "failed",
            "message": "Invalid credentials or user is not a specialist.",
        }, status=status.HTTP_401_UNAUTHORIZED)

    return Response({
        "status": "failed",
        "message": serializer.errors,
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def register_specialist(request):
    data = request.data
    serializer = CreateAccountSerializer(data=data)

    try:
        if serializer.is_valid():
            email = data.get('email')

            if not User.objects.filter(email=email).exists():
                user = User.objects.create(
                    first_name=data.get('first_name'),
                    last_name=data.get('last_name'),
                    username=email,
                    email=email,
                    password=make_password(data.get('password'))
                )
                user.profile.role = RoleChoices.SPECIALIST
                user.profile.save()

                return Response({
                    "status": "success",
                    "message": f"Successfully created your {user.profile.role} account!",
                }, status=status.HTTP_201_CREATED)

            return Response({
                "status": "failed",
                "message": "An account with this email already exists.",
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "status": "failed",
            "message": serializer.errors,
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as error:
        return Response({
            "status": "failed",
            "message": f"Error while creating account: {error}",
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_all_specialists(request):
    try:
        specialists = Profile.objects.select_related('user').filter(role=RoleChoices.SPECIALIST)
        serializer = ProfileSerializer(specialists, many=True)
        return Response({
            "status": "success",
            "specialists": serializer.data,
        }, status=status.HTTP_200_OK)

    except Exception as error:
        return Response({
            "status": "failed",
            "message": f"Error fetching specialists: {error}",
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_users(request):
    try:
        users = User.objects.filter(profile__role=RoleChoices.PATIENT).exclude(is_staff=True, is_superuser=True).select_related('profile')

        profiles = [user.profile for user in users]
        serializer = ProfileSerializer(profiles, many=True)

        return Response({
            "status": "success",
            "users": serializer.data,
        }, status=status.HTTP_200_OK)

    except Exception as error:
        return Response({
            "status": "failed",
            "message": f"Error fetching users: {error}",
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    # user_serializer = UserSerializer(request.user, many=False)
    profile_serializer = ProfileSerializer(request.user.profile, many=False)

    return Response({
        "status": "success",
        # "user": user_serializer.data,
        "profile": profile_serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_specialist_profile(request):
    user = request.user

    if user.profile.role != RoleChoices.SPECIALIST:
        raise PermissionDenied("Only specialists can update this profile.")

    serializer = ProfileSerializer(user.profile, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({
            "status": "success",
            "message": "Specialist profile updated successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    return Response({
        "status": "failed",
        "message": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_current_user(request):
    user = request.user
    profile = user.profile  

    serializer = ProfileSerializer(profile, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response({
            "status": "success",
            "message": "User profile updated successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    return Response({
        "status": "failed",
        "message": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


def get_current_host(request):
    protocol = 'https' if request.is_secure() else 'http'
    return f"{protocol}://{request.get_host()}"


@api_view(['POST'])
def user_forgot_password(request):
    data = request.data
    try:
        user = get_object_or_404(User, email=data['email'])

        token = get_random_string(40)
        expire_date = timezone.now() + timedelta(minutes=30)

        user.profile.password_reset_token = token
        user.profile.password_reset_expire = expire_date
        user.profile.save()

        host = get_current_host(request)
        link = f'{host}/api/v1/resetPassword/{token}'
        body = f"Your Password Reset Link is: {link}"

        send_mail(
            "Password Reset From Homein App",
            body,
            "homein@info.com",
            [data['email']],
        )

        return Response({
            "status": "success",
            "message": f"Password reset token sent to {data['email']}",
            "link": link
        }, status=status.HTTP_200_OK)

    except Exception as error:
        return Response({
            "status": "failed",
            "message": f"Error while processing password reset: {error}"
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def user_reset_password(request, resetToken):
    data = request.data
    try:
        user = get_object_or_404(User, profile__password_reset_token=resetToken)

        if user.profile.password_reset_expire < timezone.now():
            return Response({"error": "Reset token is expired."}, status=status.HTTP_400_BAD_REQUEST)

        if data['password'] != data['confirmPassword']:
            return Response({"error": "Passwords do not match."}, status=status.HTTP_400_BAD_REQUEST)

        user.password = make_password(data['password'])
        user.profile.password_reset_token = ""
        user.profile.password_reset_expire = None
        user.profile.save()
        user.save()

        return Response({
            "status": "success",
            "message": "Password successfully reset"
        }, status=status.HTTP_200_OK)

    except Exception as error:
        return Response({
            "status": "failed",
            "message": f"Error while resetting password: {error}"
        }, status=status.HTTP_400_BAD_REQUEST)
