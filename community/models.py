from django.db import models
import uuid
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class Posts(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, related_name="posts", on_delete=models.CASCADE)
    caption = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name="liked_posts", blank=True)
    image = models.ImageField(upload_to="posts_pics", blank=True, null=True, default=None)
    video = models.FileField(upload_to="posts_videos", blank=True, null=True, default=None)

    def like_post(self, user):
        if user in self.likes.all():
            self.likes.remove(user)
        else:
            self.likes.add(user)

    def __str__(self):
        return f"Post by {self.user.username}"


class UserSeenPosts(models.Model):
    user = models.ForeignKey(User, related_name='seen_posts', on_delete=models.CASCADE)
    post = models.ForeignKey(Posts, related_name='seen_by', on_delete=models.CASCADE)
    seen_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'post']

class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(Posts, related_name="comments", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    edited = models.BooleanField(default=False)
    
    @property
    def likes_count(self):
        return self.comment_likes.count()

    def is_liked_by(self, user):
        return self.comment_likes.filter(user=user).exists()

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post}"
    
class LikeComments(models.Model):
    user = models.ForeignKey(User, related_name='user_comment_likes', on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, related_name='comment_likes', on_delete=models.CASCADE)

    class Meta:
        unique_together = ['user', 'comment']

    def clean(self):
        if self.user == self.comment.user:
            raise ValidationError("You cannot like your own comment.")


class Reply(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    comment = models.ForeignKey(Comment, related_name="replies", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    edited = models.BooleanField(default=False)

    def __str__(self):
        return f"Reply by {self.user.username} on {self.comment}"

    
class LikeReplies(models.Model):
    user = models.ForeignKey(User, related_name='user_reply_likes', on_delete=models.CASCADE)
    reply = models.ForeignKey(Reply, related_name='reply_likes', on_delete=models.CASCADE)  # ✅ correct
    liked = models.BooleanField(default=True)

    class Meta:
        unique_together = ['user', 'reply']

    def __str__(self):
        return f"{self.user.username} likes reply {self.reply.id}"

    def clean(self):
        if self.user == self.reply.user:
            raise ValidationError("You cannot like your own reply.")


class Likes(models.Model):
    user = models.ForeignKey(User, related_name='user_likes', on_delete=models.CASCADE)
    post = models.ForeignKey(Posts, related_name='post_likes', on_delete=models.CASCADE)
    liked = models.BooleanField(default=True)

    class Meta:
        unique_together = ['user', 'post']

    def __str__(self):
        return f"{self.user.username} likes {self.post}"

    def clean(self):
        if self.user == self.post.user:
            raise ValidationError("You cannot like your own post.")



class Status(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, related_name="statuses", on_delete=models.CASCADE)
    caption = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to="status_images", blank=True, null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name="liked_statuses", blank=True)

    def like_status(self, user):
        if user in self.likes.all():
            self.likes.remove(user)
        else:
            self.likes.add(user)

    @property
    def is_expired(self):
        return self.created_at < timezone.now() - timedelta(hours=24)

    def is_seen_by(self, user):
        from .models import SeenStatus  
        return SeenStatus.objects.filter(user=user, status=self).exists()

    def __str__(self):
        return f"Status by {self.user.username}"


class StatusReply(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status = models.ForeignKey(Status, related_name="replies", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    edited = models.BooleanField(default=False)

    def __str__(self):
        return f"Reply by {self.user.username} on {self.status.id}"


class StatusLikes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.ForeignKey(Status, related_name="status_likes", on_delete=models.CASCADE)
    liked = models.BooleanField(default=True)

    class Meta:
        unique_together = ['user', 'status']

    def __str__(self):
        return f"{self.user.username} likes status {self.status.id}"


class SeenStatus(models.Model):
    user = models.ForeignKey(User, related_name='seen_statuses', on_delete=models.CASCADE)
    status = models.ForeignKey(Status, related_name='seen_by', on_delete=models.CASCADE)
    seen_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'status']

    def __str__(self):
        return f"{self.user.username} saw status {self.status.id}"
