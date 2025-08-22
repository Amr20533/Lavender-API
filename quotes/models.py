from django.db import models

class Quote(models.Model):
    text = models.TextField()
    author = models.CharField(max_length=255)
    image = models.ImageField(upload_to='quotes/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author}: {self.text[:30]}..."
