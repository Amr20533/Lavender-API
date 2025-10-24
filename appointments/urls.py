from django.urls import path
from .views import (AppointmentListView, BookingCreateView, 
                    SpecialistAnalyticsView, AvailabilityUpdateView,
                    CheckoutSessionView, SuccessfulPaymentView,
                      BookingListView, AppointmentCreateView)

urlpatterns = [
    path("appointments/", AppointmentListView.as_view(), name="appointment-list"),
    path("appointments/analytics/", SpecialistAnalyticsView.as_view(), name="appointment-analytics"),
    path("appointments/availability/", AvailabilityUpdateView.as_view(), name="update-availability"),
    path("appointments/create/", AppointmentCreateView.as_view(), name="appointment-create"),

    path("bookings/create/", BookingCreateView.as_view(), name="booking-create"),
    path("bookings/", BookingListView.as_view(), name="booking-list"),

    path('appointments/checkout/<int:appointment_id>', CheckoutSessionView.as_view(), name='checkout'),
    path('payment/success/', SuccessfulPaymentView.as_view(), name='successful_payment'),

]
