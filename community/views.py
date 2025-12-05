from django.shortcuts import render

from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *
from django.db.models import Case, When, Value, IntegerField
from account.permissions import *


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([JSONParser, MultiPartParser, FormParser])
def create_post(request):
    caption = request.data.get("caption")
    if not caption:
        return Response({"error": "Caption is required."}, status=status.HTTP_400_BAD_REQUEST)

    post = Posts.objects.create(
        user=request.user,
        caption=caption,
        image=request.data.get("image") or None,
        video=request.data.get("video") or None
    )

    return Response(
        {"status": "success", "data": PostSerializer(post).data},
        status=status.HTTP_201_CREATED
    )

@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
@parser_classes([JSONParser, MultiPartParser, FormParser])
def edit_post(request, post_id):
    try:
        post = Posts.objects.get(id=post_id, user=request.user)
    except Posts.DoesNotExist:
        return Response({"error": "Post not found or not yours."}, status=status.HTTP_404_NOT_FOUND)

    caption = request.data.get("caption", post.caption)
    image = request.data.get("image", post.image)
    video = request.data.get("video", post.video)

    post.caption = caption
    post.image = image if image != "" else None
    post.video = video if video != "" else None
    post.save()

    return Response(
        {"status": "success", "data": PostSerializer(post).data},
        status=status.HTTP_200_OK
    )


# @api_view(['GET'])
# def get_posts(request):
#     user = request.user

#     # exclude posts already seen by this user
#     seen_post_ids = UserSeenPosts.objects.filter(user=user).values_list('post_id', flat=True)
#     new_posts = Posts.objects.exclude(id__in=seen_post_ids).order_by("-created_at")

#     # mark these posts as seen
#     for post in new_posts:
#         UserSeenPosts.objects.get_or_create(user=user, post=post)

#     serializer = PostSerializer(new_posts, many=True)
#     return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_posts(request):
    user = request.user

    posts = Posts.objects.all()
    serializer = PostSerializer(posts, many=True, context={'request': request})
    return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def like_post(request, post_id):
    try:
        post = Posts.objects.get(id=post_id)
    except Posts.DoesNotExist:
        return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

    user = request.user

    if user in post.likes.all():
        post.likes.remove(user)
        return Response({
            "status": "success",
            "likes": []
        }, status=status.HTTP_200_OK)
    else:
        post.likes.add(user)
        liked_users = post.likes.all().values("id", "username", "email")
        return Response({
            "status": "success",
            "likes": list(liked_users)  
        }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_comment(request, post_id):
    try:
        post = Posts.objects.get(id=post_id)
    except Posts.DoesNotExist:
        return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

    content = request.data.get("content")
    if not content:
        return Response({"error": "Content is required."}, status=status.HTTP_400_BAD_REQUEST)

    comment = Comment.objects.create(post=post, user=request.user, content=content)
    return Response({"status": "success", "data": CommentSerializer(comment).data}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def like_comment(request, comment_id):
    try:
        comment = Comment.objects.get(id=comment_id)
    except Comment.DoesNotExist:
        return Response({"error": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)

    # Create or toggle like
    like, created = LikeComments.objects.get_or_create(user=request.user, comment=comment)
    if not created:
        like.delete()

    # Check if current user now likes the comment
    is_liked = LikeComments.objects.filter(user=request.user, comment=comment).exists()

    return Response({
        "status": "success",
        "likes_count": comment.comment_likes.count(),
        "is_liked": is_liked
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_post_comments(request, post_id):
    try:
        post = Posts.objects.get(id=post_id)
    except Posts.DoesNotExist:
        return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

    comments = post.comments.all().order_by("-created_at")
    serializer = CommentSerializer(comments, many=True, context={"request": request})
    return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def edit_comment(request, comment_id):
    try:
        comment = Comment.objects.get(id=comment_id, user=request.user)
    except Comment.DoesNotExist:
        return Response({"error": "Comment not found or unauthorized"}, status=status.HTTP_404_NOT_FOUND)

    content = request.data.get("content")
    if not content:
        return Response({"error": "Content is required"}, status=status.HTTP_400_BAD_REQUEST)

    comment.content = content
    comment.edited = True
    comment.save()

    return Response({"status": "success", "data": CommentSerializer(comment).data}, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_reply(request, comment_id):
    try:
        comment = Comment.objects.get(id=comment_id)
    except Comment.DoesNotExist:
        return Response({"error": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)

    content = request.data.get("content")
    if not content:
        return Response({"error": "Content is required."}, status=status.HTTP_400_BAD_REQUEST)

    reply = Reply.objects.create(comment=comment, user=request.user, content=content)
    return Response({"status": "success", "data": ReplySerializer(reply).data}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def like_reply(request, reply_id):
    try:
        reply = Reply.objects.get(id=reply_id)
    except Reply.DoesNotExist:
        return Response({"error": "Reply not found"}, status=status.HTTP_404_NOT_FOUND)

    like, created = LikeReplies.objects.get_or_create(user=request.user, reply=reply)

    if not created:
        like.delete()
        return Response({"status": "success", "likes_count": reply.reply_likes.count()}, status=status.HTTP_200_OK)

    return Response({"status": "success", "likes_count": reply.reply_likes.count()}, status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def edit_reply(request, reply_id):
    try:
        reply = Reply.objects.get(id=reply_id, user=request.user)
    except Reply.DoesNotExist:
        return Response({"error": "Reply not found or unauthorized"}, status=status.HTTP_404_NOT_FOUND)

    content = request.data.get("content")
    if not content:
        return Response({"error": "Content is required"}, status=status.HTTP_400_BAD_REQUEST)

    reply.content = content
    reply.edited = True
    reply.save()

    return Response({"status": "success", "data": ReplySerializer(reply).data}, status=status.HTTP_200_OK)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_comment_replies(request, comment_id):
    try:
        comment = Comment.objects.get(id=comment_id)
    except Comment.DoesNotExist:
        return Response({"error": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)

    replies = comment.replies.all().order_by("created_at")  # oldest first
    serializer = ReplySerializer(replies, many=True)
    return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsUserOrSpecialist])
@parser_classes([JSONParser, MultiPartParser, FormParser])
def create_status(request):
    caption = request.data.get("caption")
    image = request.data.get("image")

    status_obj = Status.objects.create(
        user=request.user,
        caption=caption,
        image=image
    )

    serializer = StatusSerializer(status_obj, context={"request": request})

    return Response(
        {"status": "success", "data": serializer.data},
        status=status.HTTP_201_CREATED,
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def like_status(request, status_id):
    try:
        status_obj = Status.objects.get(id=status_id)
    except Status.DoesNotExist:
        return Response({"error": "Status not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.user in status_obj.likes.all():
        status_obj.likes.remove(request.user)
        return Response({"status": "unliked", "likes_count": status_obj.likes.count()})
    else:
        status_obj.likes.add(request.user)
        return Response({"status": "liked", "likes_count": status_obj.likes.count()})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reply_status(request, status_id):
    try:
        status_obj = Status.objects.get(id=status_id)
    except Status.DoesNotExist:
        return Response({"error": "Status not found"}, status=status.HTTP_404_NOT_FOUND)

    content = request.data.get("content")
    if not content:
        return Response({"error": "Content is required."}, status=status.HTTP_400_BAD_REQUEST)

    reply = StatusReply.objects.create(
        status=status_obj,
        user=request.user,
        content=content
    )

    return Response({"status": "success", "data": StatusReplySerializer(reply).data}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_status_feed(request):
    now = timezone.now()
    
    # Get all statuses in last 24 hours
    statuses = Status.objects.filter(created_at__gte=now - timedelta(hours=24))
    
    # Mark as seen
    for s in statuses:
        SeenStatus.objects.get_or_create(user=request.user, status=s)
    
    # Group by user
    users_with_statuses = User.objects.filter(statuses__in=statuses).distinct()
    
    # Optional: prioritize current user first
    users_with_statuses = users_with_statuses.annotate(
        is_current_user=Case(
            When(id=request.user.id, then=Value(0)),
            default=Value(1),
            output_field=IntegerField()
        )
    ).order_by("is_current_user")
    
    serializer = UserStatusSerializer(users_with_statuses, many=True, context={"request": request})
    return Response({"status": "success", "data": serializer.data})
