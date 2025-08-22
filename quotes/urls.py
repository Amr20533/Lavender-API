from django.urls import path
from .views import daily_quote, create_quote

urlpatterns = [
    path('quote/daily/', daily_quote, name='daily_quote'),
    path('quote/create/', create_quote, name='create_quote'),
]
