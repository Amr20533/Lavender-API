from rest_framework import serializers
from .models import Posts, Comment, Reply, Status, StatusReply
from django.contrib.auth.models import User


class ReplySerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField(read_only=True)
    likes_count = serializers.SerializerMethodField()

    class Meta:
        model = Reply
        fields = ["id", "comment", "user", "content", "created_at", "edited", "likes_count"]

    def get_user(self, obj):
        return obj.user.id  # ✅ user id

    def get_likes_count(self, obj):
        return obj.reply_likes.count()


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ["id", "post", "user", "content", "created_at", "edited", "likes_count", "is_liked"]

    def get_user(self, obj):
        return obj.user.id

    def get_likes_count(self, obj):
        return obj.comment_likes.count()

    def get_is_liked(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.comment_likes.filter(user=request.user).exists()
        return False

class PostSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField(read_only=True)
    likes_count = serializers.SerializerMethodField()
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Posts
        fields = [
            "id",
            "user",
            "caption",
            "created_at",
            "likes_count",
            "image",
            "video",
            "comments",
        ]

    def get_likes_count(self, obj):
        return obj.likes.count()

class PostSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField(read_only=True)
    likes_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Posts
        fields = [
            "id",
            "user",
            "caption",
            "created_at",
            "likes_count",
            "is_liked",   
            "image",
            "video",
            "comments",
        ]

    def get_user(self, obj):
        return obj.user.id

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_is_liked(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.likes.filter(id=request.user.id).exists()
        return False

class StatusReplySerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = StatusReply
        fields = ["id", "status", "user", "content", "created_at", "edited"]

class UserStatusSerializer(serializers.ModelSerializer):
    statuses = serializers.SerializerMethodField()
    profile_pic = serializers.SerializerMethodField()  # New field

    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "profile_pic", "statuses"]

    def get_statuses(self, user):
        # Get all statuses for this user ordered by created_at
        statuses = Status.objects.filter(user=user).order_by('-created_at')
        return StatusSerializer(statuses, many=True, context=self.context).data

    def get_profile_pic(self, user):
        # Example: if User has a related profile model with a profile_pic field
        if hasattr(user, 'profile') and user.profile.profile_pic:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(user.profile.profile_pic.url)
            return user.profile.profile_pic.url
        return None


class StatusSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    likes_count = serializers.SerializerMethodField()
    is_seen = serializers.SerializerMethodField()
    replies = StatusReplySerializer(many=True, read_only=True)

    class Meta:
        model = Status
        fields = ["id", "user", "caption", "image", "created_at", "likes_count", "is_seen", "replies"]

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_is_seen(self, obj):
        user = self.context.get("request").user
        return obj.is_seen_by(user)


