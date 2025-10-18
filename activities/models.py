from django.db import models
from django.contrib.auth.models import User
from programs.models import * 

class Favorite(models.Model):
    user = models.ForeignKey(User, related_name='favorites', on_delete=models.CASCADE)
    specialist = models.ForeignKey('account.Profile', related_name='favorited_by', on_delete=models.CASCADE)
    in_favorite = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'specialist')

    def __str__(self):
        return f"{self.user.email} -> {self.specialist.user.email}"

class Review(models.Model):
    user = models.ForeignKey(User, related_name='reviews', on_delete=models.CASCADE)
    specialist = models.ForeignKey('account.Profile', related_name='reviews', on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'specialist')

    def __str__(self):
        return f"Review by {self.user.email} -> {self.specialist.user.email} ({self.rating})"


class CourseReview(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    user = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='course_reviews'
    )
    rating = models.PositiveIntegerField(default=5)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('course', 'user')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.user.first_name} → {self.course.title} ({self.rating})"
