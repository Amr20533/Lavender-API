from rest_framework import serializers
from .models import Profile, SpecialtyChoices
from django.contrib.auth.models import User
from appointments.serializers import AppointmentSerializer


class CreateAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = User 
        fields = ('first_name', 'last_name', 'email', 'password')
        extra_keywords = {
            'first_name': {'requied': True, 'allow_blank' : False}, 
            'last_name': {'requied': True, 'allow_blank' : False}, 
            'email' : {'requied': True, 'allow_blank' : False}, 
            'password' : {'requied': True, 'allow_blank' : False, 'min-length' : 8}
        }

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name']
        read_only_fields = ['id', 'username', 'email']

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    specialty_display = serializers.CharField(source='get_specialty_display', read_only=True)
    extra_specialty_display = serializers.CharField(source='get_extra_specialty_display', read_only=True)
    appointments = AppointmentSerializer(many=True, read_only=True)

    class Meta:
        model = Profile
        fields = [
            # 'id',
            'user',
            'profile_pic',
            'date_of_birth',
            'gender',
            'phone_number',
            'role',
            'bio',
            'country',
            'years_of_experience',
            'price_per_hour',
            'avg_rating',
            'speciality',
            'specialty_display',
            'extra_specialty',
            'extra_specialty_display',
            "appointments",
        ]
        read_only_fields = ['role']

    def update(self, instance, validated_data):
        # Update user
        user_data = validated_data.pop('user', {})
        for attr, value in user_data.items():
            setattr(instance.user, attr, value)
        instance.user.save()

        # Update profile
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance

    def to_representation(self, instance):
        data = super().to_representation(instance)
        
        if instance.role != 'specialist':
            data.pop('experience', None)
            data.pop('price_per_hour', None)
            data.pop('speciality', None)
            data.pop('specialty_display', None)
            data.pop('extra_specialty', None)
            data.pop('extra_specialty_display', None)
            data.pop('avg_rating', None)
            data.pop('appointments', None)

        return data

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
