from django.urls import path
from .views import AppointmentListView, AppointmentCreateView, SpecialistAnalyticsView, AvailabilityUpdateView

urlpatterns = [
    path("appointments/", AppointmentListView.as_view(), name="appointment-list"),
    # path("appointments/create/", AppointmentCreateView.as_view(), name="appointment-create"),
    path("appointments/analytics/", SpecialistAnalyticsView.as_view(), name="appointment-analytics"),
    path("appointments/availability/", AvailabilityUpdateView.as_view(), name="update-availability"),

]
