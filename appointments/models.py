from django.utils import timezone
from django.db import models

class Appointment(models.Model):
    profile = models.ForeignKey("account.Profile", related_name="appointments", on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_booked = models.BooleanField(default=False)

    class Meta:
        unique_together = ("profile", "date", "start_time")

    @property
    def price(self):
        return self.profile.price_per_hour or 0

    def __str__(self):
        return f"{self.profile.user.email} - {self.date} {self.start_time}-{self.end_time}"

    # ✅ Helper querysets
    @classmethod
    def previous_for_profile(cls, profile):
        today = timezone.now().date()
        return cls.objects.filter(profile=profile).filter(models.Q(date__lt=today) | models.Q(is_booked=True))

    @classmethod
    def available_for_profile(cls, profile):
        today = timezone.now().date()
        return cls.objects.filter(profile=profile, is_booked=False, date__gte=today)
