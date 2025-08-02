from django.urls import path
from .views import *

urlpatterns = [
    path('specialist/favorites/', list_favorites, name='list_favorites'),
    path('specialist/favorites/add/', add_to_favorites, name='add_to_favorites'),
    path('specialist/favorites/remove/<int:specialist_id>/', remove_favorite, name='remove_favorite'),
    path('specialist/review/add/', create_review, name='add_review'),
    path('specialist/<int:specialist_id>/reviews/', get_reviews, name='get_reviews'),
    path('specialist/<int:specialist_id>/reviews/delete/', delete_review, name='delete_review'),

]
