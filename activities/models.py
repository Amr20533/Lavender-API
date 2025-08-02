from django.db import models
from django.contrib.auth.models import User

class Favorite(models.Model):
    user = models.ForeignKey(User, related_name='favorites', on_delete=models.CASCADE)
    specialist = models.ForeignKey('account.Profile', related_name='favorited_by', on_delete=models.CASCADE)
    in_favorite = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'specialist')

    def __str__(self):
        return f"{self.user.email} -> {self.specialist.user.email}"
