from rest_framework import serializers
from .models import Appointment, Booking
from account.models import Profile


class AppointmentSerializer(serializers.ModelSerializer):
    profile = serializers.StringRelatedField(read_only=True)  # show specialist email
    price = serializers.DecimalField(source="profile.price_per_hour", 
                                     read_only=True, 
                                     max_digits=6, 
                                     decimal_places=2)

    class Meta:
        model = Appointment
        fields = ["id", "profile", "date", "start_time", "end_time", "price", "is_booked"]


class AvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["working_days", "start_time", "end_time"]

    def update(self, instance, validated_data):
        instance.working_days = validated_data.get("working_days", instance.working_days)
        instance.start_time = validated_data.get("start_time", instance.start_time)
        instance.end_time = validated_data.get("end_time", instance.end_time)
        instance.save()
        return instance

class AppointmentAnalyticsSerializer(serializers.Serializer):
    prev_count = serializers.IntegerField()
    available_count = serializers.IntegerField()
    prev_appointments = serializers.SerializerMethodField()
    available_appointments = serializers.SerializerMethodField()

    def get_prev_appointments(self, obj):
        return [
            f"{appt.date} {appt.start_time}-{appt.end_time}"
            for appt in obj["prev_appointments"]
        ]

    def get_available_appointments(self, obj):
        return [
            f"{appt.date} {appt.start_time}-{appt.end_time}"
            for appt in obj["available_appointments"]
        ]

class BookingSerializer(serializers.ModelSerializer):
    specialist = serializers.CharField(source="appointment.profile.user.email", read_only=True)
    appointment_time = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = ["id", "patient", "specialist", "appointment", "appointment_time", "is_paid","booked_at"]
        read_only_fields = ["patient", "is_paid", "booked_at"]

    def get_appointment_time(self, obj):
        return f"{obj.appointment.date} {obj.appointment.start_time}-{obj.appointment.end_time}"

    def create(self, validated_data):
        request = self.context["request"]
        validated_data["patient"] = request.user.profile

        appointment = validated_data["appointment"]

        if appointment.is_booked:
            raise serializers.ValidationError("This appointment is already booked.")

        # mark appointment as booked
        appointment.is_booked = True
        appointment.save()

        booking = super().create(validated_data)
        return booking
