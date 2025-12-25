from django.db import models
from django.contrib.auth.models import User
from account.models import *
from django.utils import timezone

class ChatBubble(models.Model):
    sender = models.ForeignKey(User, on_delete = models.CASCADE, related_name = "sender", default = 0)
    receiver = models.ForeignKey(User, on_delete = models.CASCADE, related_name = "receiver", default=1)
    message = models.CharField(max_length = 2000, null = True)
    is_read = models.BooleanField(default = False)
    timestamp = models.DateTimeField(auto_now_add = True)

    class Meta:
        ordering = ['timestamp']
        verbose_name_plural = "Messages"

    def __str__(self):
        return f"{self.receiver} - {self.sender}"
    
    @property
    def senderProfile(self):
        return self.sender.profile  

    @property
    def receiverProfile(self):
        return self.receiver.profile 
    

class ReadReceipt(models.Model):
    message = models.ForeignKey(
        'ChatBubble', 
        on_delete=models.CASCADE, 
        related_name='receipts'
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='read_receipts'
    )
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('message', 'user')
        ordering = ['-read_at']

    def __str__(self):
        return f"{self.user.username} read message {self.message.id}"