from django.urls import path
from .views import (
    QuizListView, QuizDetailView,
    SubmitAnswerView, SubmitQuizResultView, QuizResultView, MusicCardListCreateView, MusicCardDetailView
)

urlpatterns = [
    path("music/", MusicCardListCreateView.as_view(), name="music-list"),
    path("music/<uuid:id>/", MusicCardDetailView.as_view(), name="music-detail"),
    path("quizzes/", QuizListView.as_view(), name="quiz-list"),
    path("quizzes/<uuid:pk>/", QuizDetailView.as_view(), name="quiz-detail"),
    path("answers/submit/", SubmitAnswerView.as_view(), name="submit-answer"),
    path("quizzes/<uuid:quiz_id>/submit/", SubmitQuizResultView.as_view(), name="submit-quiz-result"),
    path("quizzes/<uuid:quiz_id>/result/", QuizResultView.as_view(), name="quiz-result"),

]

