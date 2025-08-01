from django.urls import path
from .views import *

urlpatterns = [
    path('answers/', SubmitAnswerViewSet.as_view({'post': 'create'}), name='submit_answer'),
    path('questions/', IntroQuestionViewSet.as_view({'get': 'list'}), name='get_questions'),
]
