import uuid
import datetime
from django.db import models
from django.contrib.auth.models import User
from account.models import Profile

class MusicCard(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200, default="None", blank=False)
    author = models.CharField(max_length=180, default="N/A", blank=False)
    album = models.CharField(max_length=200, default="Single", blank=True)
    album_cover = models.ImageField(upload_to="music_covers/",default="music_covers\music_cover.png", blank=True, null=True)
    audio_file = models.FileField(upload_to="music_files/", blank=True, null=True)
    # duration stored as DurationField and will be filled automatically
    duration = models.DurationField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.author} - {self.title} ({self.album})"

    def save(self, *args, **kwargs):
        """
        Save first to ensure the file exists on disk, then compute duration (if a new file was uploaded)
        """
        # Determine if audio file changed
        audio_changed = False
        try:
            if self.pk:
                old = MusicCard.objects.get(pk=self.pk)
                old_name = old.audio_file.name if old.audio_file else None
                new_name = self.audio_file.name if self.audio_file else None
                audio_changed = new_name and new_name != old_name
            else:
                # new instance with file
                audio_changed = bool(self.audio_file)
        except MusicCard.DoesNotExist:
            audio_changed = bool(self.audio_file)

        # Save first so file is present on disk for mutagen
        super().save(*args, **kwargs)

        if audio_changed and self.audio_file:
            try:
                # compute duration using mutagen
                from mutagen import File as MutagenFile

                file_path = self.audio_file.path  # requires local FS
                audio = MutagenFile(file_path)
                length_secs = getattr(audio.info, "length", None)
                if length_secs is not None:
                    # round or keep fractional seconds as you like
                    self.duration = datetime.timedelta(seconds=round(length_secs))
                    # update only the duration field to avoid recursion
                    MusicCard.objects.filter(pk=self.pk).update(duration=self.duration)
            except Exception:
                # silently fail or log — don't block saves on duration error
                # you can use logging.warning(...) here
                pass


class PsychoMeasurementQuiz(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to="quizzez/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class QuizQuestion(models.Model):
    quiz = models.ForeignKey(PsychoMeasurementQuiz, related_name="questions", on_delete=models.CASCADE)
    text = models.CharField(max_length=500)
    order = models.PositiveIntegerField(default=0) 

    def __str__(self):
        return f"{self.quiz.title} - {self.text}"


class QuizAnswer(models.Model):
    question = models.ForeignKey(QuizQuestion, related_name="answers", on_delete=models.CASCADE)
    text = models.CharField(max_length=300)
    score = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.question.text} → {self.text} ({self.score})"


class UserAnswer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE)
    answer = models.ForeignKey(QuizAnswer, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("user", "question")

    def __str__(self):
        return f"{self.user} answered {self.answer.text} for {self.question.text}"


class QuizResultCategory(models.Model):
    quiz = models.ForeignKey(PsychoMeasurementQuiz, related_name="result_categories", on_delete=models.CASCADE)
    min_score = models.IntegerField()
    max_score = models.IntegerField()
    title = models.CharField(max_length=255)     
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.quiz.title}: {self.title} ({self.min_score}-{self.max_score})"


class QuizResult(models.Model):
    quiz = models.ForeignKey(PsychoMeasurementQuiz, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_score = models.IntegerField()
    percentage = models.FloatField()
    title = models.CharField(max_length=255) 
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("quiz", "user") 

    def __str__(self):
        return f"{self.user} → {self.quiz.title}: {self.title}"


class Course(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    instructor = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='courses',
        limit_choices_to={'role': 'SPECIALIST'},
        help_text="Only specialists can create courses."
    )
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='courses/images/', blank=True, null=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    duration = models.PositiveIntegerField(default=0, help_text="Duration in minutes.")
    total_sessions = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def update_sessions_count(self):
        self.total_sessions = self.videos.count()
        self.save()

    def __str__(self):
        return self.title


class CourseVideo(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='videos'
    )
    title = models.CharField(max_length=255)
    video_url = models.URLField()
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Enrollment(models.Model):
    """Tracks which user has access to which course."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    is_paid = models.BooleanField(default=False)
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'course')

    def __str__(self):
        return f"{self.user.user.email} -> {self.course.title} ({'Paid' if self.is_paid else 'Locked'})"
