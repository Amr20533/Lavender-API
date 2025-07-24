from django.db import models
import uuid
from django.conf import settings

class IntroQuestion(models.Model):
    SINGLE = 'single'
    MULTIPLE = 'multiple'
    QUESTION_TYPE_CHOICES = [
        (SINGLE, 'Single Answer (Text or Single Choice)'),
        (MULTIPLE, 'Multiple Choices'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.CharField(max_length=500, default="", blank=True)
    type = models.CharField(max_length=10, choices=QUESTION_TYPE_CHOICES, default=SINGLE)
    description = models.TextField(blank=True, default="")

    def __str__(self):
        return self.question


class IntroOption(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.ForeignKey(IntroQuestion, related_name='options', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    parentQuestions = models.ForeignKey('self', null=True, blank=True, related_name='children', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('question', 'text', 'parentQuestions')

    def __str__(self):
        return self.text


class IntroAnswer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    question = models.ForeignKey(IntroQuestion, on_delete=models.CASCADE, related_name='answers')
    
    # For text answers
    text_answer = models.TextField(blank=True, null=True)

    # For selected options (single or multi)
    selected_options = models.ManyToManyField(IntroOption, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'question')

    def __str__(self):
        return f"Answer by {self.user} to '{self.question}'"
