from rest_framework import generics, permissions
from .models import Appointment
from .serializers import AppointmentSerializer, AppointmentCreateSerializer, AvailabilitySerializer
from .serializers import AppointmentAnalyticsSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from .utils import generate_slots_for_profile  
from account.permissions import IsSpecialist


class AppointmentListView(generics.ListAPIView):
    queryset = Appointment.objects.filter(is_booked=False)
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.AllowAny]


class AppointmentCreateView(generics.CreateAPIView):
    serializer_class = AppointmentCreateSerializer
    permission_classes = [permissions.IsAuthenticated, IsSpecialist]

    def perform_create(self, serializer):
        profile = self.request.user.profile
        serializer.save(
            profile=profile,
            price=profile.price_per_hour
        )

class AvailabilityUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = AvailabilitySerializer
    permission_classes = [permissions.IsAuthenticated, IsSpecialist]

    def get_object(self):
        return self.request.user.profile 

    def perform_update(self, serializer):
        profile = serializer.save()
        generate_slots_for_profile(profile, weeks_ahead=4)

class SpecialistAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = request.user.profile
        prev_appointments = Appointment.previous_for_profile(profile)
        available_appointments = Appointment.available_for_profile(profile)

        data = {
            "prev_count": prev_appointments.count(),
            "available_count": available_appointments.count(),
            "prev_appointments": prev_appointments[:10],      # limit for readability
            "available_appointments": available_appointments[:10],
        }
        serializer = AppointmentAnalyticsSerializer(data)
        return Response(serializer.data)
