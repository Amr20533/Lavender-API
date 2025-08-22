from django.urls import path
from .views import (
    create_post, edit_post, get_posts, like_post,
    add_comment, edit_comment, like_comment,
    add_reply, edit_reply, like_reply, get_post_comments, get_comment_replies,
    create_status, like_status, get_status_feed, reply_status
)

urlpatterns = [
    # Posts
    path("posts/create/", create_post, name="create_post"),
    path("posts/<uuid:post_id>/edit/", edit_post, name="edit_post"),
    path("posts/", get_posts, name="get_posts"),
    path("posts/<uuid:post_id>/like/", like_post, name="like_post"),

    # Comments
    path("posts/<uuid:post_id>/comments/add/", add_comment, name="add_comment"),
    path("comments/<uuid:comment_id>/edit/", edit_comment, name="edit_comment"),
    path("comments/<uuid:comment_id>/like/", like_comment, name="like_comment"),
    path("posts/<uuid:post_id>/comments/", get_post_comments, name="get_post_comments"),

    # Replies
    path("comments/<uuid:comment_id>/replies/add/", add_reply, name="add_reply"),
    path("replies/<uuid:reply_id>/edit/", edit_reply, name="edit_reply"),
    path("replies/<uuid:reply_id>/like/", like_reply, name="like_reply"),
    path("comments/<uuid:comment_id>/replies/", get_comment_replies, name="get_comment_replies"),

    # Status
    path('status/create/', create_status, name='create_status'),
    path('status/<uuid:status_id>/like/', like_status, name='like_status'),
    path('status/<uuid:status_id>/reply/', reply_status, name='reply_status'),
    path('status/feed/', get_status_feed, name='status_feed'),

]
