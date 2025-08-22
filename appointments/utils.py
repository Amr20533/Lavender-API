from datetime import timedelta, datetime
from django.utils import timezone
import calendar
from appointments.models import Appointment

def generate_slots_for_profile(profile, weeks_ahead=1):
    """
    Generate slots for the given profile for the next `weeks_ahead` weeks.
    """
    today = timezone.now().date()

    for week in range(weeks_ahead):
        for day_name in profile.working_days:
            weekday_index = list(calendar.day_name).index(day_name)
            days_ahead = (weekday_index - today.weekday() + 7) % 7
            target_date = today + timedelta(days=days_ahead) + timedelta(weeks=week)

            start = datetime.combine(target_date, profile.start_time)
            end = datetime.combine(target_date, profile.end_time)

            slot_start = start
            while slot_start + timedelta(hours=1) <= end:
                slot_end = slot_start + timedelta(hours=1)
                Appointment.objects.get_or_create(
                    profile=profile,
                    date=target_date,
                    start_time=slot_start.time(),
                    end_time=slot_end.time(),
                )
                slot_start = slot_end
