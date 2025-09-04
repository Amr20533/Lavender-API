from django.urls import path
from .views import *

urlpatterns = [
    path(
        'answers/',
        SubmitAnswerViewSet.as_view({'post': 'create', 'get': 'list'}),
        name='answers'
    ),
    
    path('questions/', IntroQuestionViewSet.as_view({'get': 'list'}), name='get_questions'),
]
