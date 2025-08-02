from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from rest_framework import serializers
import re
from django.core.exceptions import ValidationError

class GenderChoices(models.TextChoices):
    MALE = 'Male', 'Male'
    FEMALE = 'Female', 'Female'
    NONE = 'None', 'None'

class RoleChoices(models.TextChoices):
    PATIENT = 'patient', 'Patient'
    SPECIALIST = 'specialist', 'Specialist'

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


class SpecialtyChoices(models.TextChoices):
    PSYCHOLOGIST = 'اخصائي نفسية', 'اخصائي نفسية'
    FAMILY_COUNSELOR = 'استشاري علاقات اسرية', 'استشاري علاقات اسرية'
    AUTISM_SPECIALIST = 'اخصائي التوحد', 'اخصائي التوحد'
    ADHD_SPECIALIST = 'اخصائي ADHD', 'اخصائي ADHD'
    PRIVATE_COUNSELING = 'مشورة سرية', 'مشورة سرية'
    CHILD_EDUCATION = 'اخصائي تربوي للاطفال', 'اخصائي تربوي للاطفال'
    CLINICAL_PSYCHOLOGIST = 'اخصائي نفسي', 'اخصائي نفسي'
    FAMILY_ISSUES = 'اخصائي مشاكل اسرية', 'اخصائي مشاكل اسرية'
    ADDICTION_THERAPIST = 'اخصائي علاج الادمان', 'اخصائي علاج الادمان'
    MARRIAGE_COUNSELOR = 'استشاري علاقات زوجية', 'استشاري علاقات زوجية'
    TRAUMA_THERAPIST = 'اخصائي صدمات نفسية', 'اخصائي صدمات نفسية'
    CHILD_PSYCHOLOGIST = 'اخصائي نفسي للاطفال', 'اخصائي نفسي للاطفال'
    BEHAVIOR_THERAPIST = 'اخصائي سلوك', 'اخصائي سلوك'
    GROUP_THERAPIST = 'اخصائي العلاج الجماعي', 'اخصائي العلاج الجماعي'
    DEPRESSION_SPECIALIST = 'اخصائي اكتئاب وقلق', 'اخصائي اكتئاب وقلق'
    PERSONALITY_THERAPIST = 'اخصائي اضطرابات الشخصية', 'اخصائي اضطرابات الشخصية'
    OCCUPATIONAL_THERAPIST = 'اخصائي علاج وظيفي', 'اخصائي علاج وظيفي'
    SPEECH_THERAPIST = 'اخصائي نطق وتخاطب', 'اخصائي نطق وتخاطب'
    LIFE_COACH = 'مدرب حياة', 'مدرب حياة'
    OTHER = 'other', 'Other'


class Profile(models.Model):
    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='profile_pics/', default='profile_pics/default_profile.jpg')
    date_of_birth = models.DateTimeField(null=True, blank=True)
    gender = models.CharField(max_length=7, default=GenderChoices.NONE, blank=True, choices=GenderChoices.choices)
    phone_number = models.CharField(max_length=11, default='', blank=True)
    password_reset_otp = models.CharField(max_length=6, default="", blank=True)
    password_reset_expire = models.DateTimeField(null=True, blank=True)
    role = models.CharField(max_length=10, choices=RoleChoices.choices, default=RoleChoices.PATIENT)
    bio = models.TextField(blank=True)
    country = models.CharField(max_length=100, blank=True)
    years_of_experience = models.PositiveIntegerField(null=True, blank=True, help_text="Years of experience")
    price_per_hour = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    specialty = models.CharField(max_length=50, choices=SpecialtyChoices.choices, blank=True)
    extra_specialty = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.user.email

    def clean(self):
        super().clean()
        if self.phone_number:
            if not re.match(r'^\d+$', self.phone_number):
                raise ValidationError("Phone Number must contain only digits.")
            if len(self.phone_number) != 11:
                raise ValidationError("Phone number must be exactly 11 digits.")
    
    @property
    def avg_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            return round(sum(r.rating for r in reviews) / reviews.count(), 1)
        return 0.0

@receiver(post_save, sender=User)
def save_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
