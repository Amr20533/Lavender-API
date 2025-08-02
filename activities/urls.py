from django.urls import path
from .views import add_to_favorites, list_favorites, remove_favorite

urlpatterns = [
    path('specialist/favorites/', list_favorites, name='list_favorites'),
    path('specialist/favorites/add/', add_to_favorites, name='add_to_favorites'),
    path('specialist/favorites/remove/<int:specialist_id>/', remove_favorite, name='remove_favorite'),
]
