from rest_framework import serializers
from .models import Posts, Comment, Reply, Status, StatusReply


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
    user = serializers.SerializerMethodField(read_only=True)
    likes_count = serializers.SerializerMethodField()
    replies = ReplySerializer(many=True, read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "post", "user", "content", "created_at", "edited", "likes_count", "replies"]

    def get_user(self, obj):
        return obj.user.id 

    def get_likes_count(self, obj):
        return obj.comment_likes.count()

    def get_replies_count(self, obj):
        return obj.replies.count()

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

