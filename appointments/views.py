from rest_framework import generics, permissions
from .models import Appointment, Booking
from .serializers import AppointmentSerializer, AvailabilitySerializer, BookingSerializer,AppointmentAnalyticsSerializer
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from .utils import generate_slots_for_profile  
from account.permissions import IsSpecialist
from account.models import Profile 
from rest_framework.response import Response
from rest_framework import status
import stripe
from django.conf import settings  
from django.views.generic import TemplateView
from rest_framework.views import APIView
from decimal import Decimal, InvalidOperation
stripe.api_key = settings.STRIPE_SECRET_KEY

class AppointmentListView(generics.ListAPIView):
    queryset = Appointment.objects.filter(is_booked=False)
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.AllowAny]

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


class BookingCreateView(generics.CreateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()

class BookingListView(generics.ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(patient=self.request.user.profile).order_by("-booked_at")


class SuccessfulPaymentView(TemplateView):
    template_name = 'index.html'
    
class CheckoutSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, appointment_id):
        try:
            appointment = Appointment.objects.get(id=appointment_id, is_booked=False)

            MAX_STRIPE_AMOUNT = Decimal("999999.99")
            quantity = int(request.data.get("quantity", 1))
            if quantity <= 0:
                return Response({"error": "Quantity must be positive."}, status=400)

            # Price conversion
            try:
                starting_price_str = str(appointment.price).strip()
                starting_price = Decimal(starting_price_str.replace(",", ""))
                total_price = starting_price * quantity
                if total_price > MAX_STRIPE_AMOUNT:
                    total_price = MAX_STRIPE_AMOUNT
                    quantity = 1
            except (InvalidOperation, ValueError, TypeError):
                return Response({"error": "Invalid price format."}, status=400)

            # Stripe line items
            line_items = [{
                "price_data": {
                    "currency": "usd",
                    "unit_amount": int(total_price * 100),
                    "product_data": {
                        "name": f"Appointment with {appointment.profile.user.get_full_name()}",
                        "description": f"Specialist: {appointment.profile.speciality}, Date: {appointment.date}, Time: {appointment.start_time}-{appointment.end_time}"
                    },
                },
                "quantity": quantity,
            }]

            session_metadata = {
                "appointment_id": str(appointment.id),
                "user_id": str(request.user.id)
            }

            checkout_session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=line_items,
                mode="payment",
                metadata=session_metadata,
                success_url=settings.SITE_URL + "api/v1/payment/success/",
                cancel_url=settings.SITE_URL + "api/v1/payment/cancel/"
            )

            # 👉 Save pending booking
            booking = Booking.objects.create(
                patient=request.user.profile,
                appointment=appointment,
                is_paid= True,
                payment_reference=checkout_session.id
            )

            appointment.is_booked = True
            appointment.save()

            return Response({
                "status": "success",
                "url": checkout_session.url,
            }, status=200)

        except Appointment.DoesNotExist:
            return Response({"error": "Appointment not found."}, status=404)
        except stripe.error.StripeError as e:
            return Response({"error": f"Stripe error: {str(e)}"}, status=400)
        except Exception as e:
            return Response({"error": str(e)}, status=500)
