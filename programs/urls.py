from django.urls import path
from .views import (
    QuizListView, QuizDetailView,
    SubmitAnswerView, SubmitQuizResultView, QuizResultView, MusicCardListCreateView, MusicCardDetailView,
    CheckoutCourseSessionView, SuccessfulCoursePaymentView, CourseViewSet, EnrollmentViewSet
)

urlpatterns = [
    path("music/", MusicCardListCreateView.as_view(), name="music-list"),
    path("music/<uuid:id>/", MusicCardDetailView.as_view(), name="music-detail"),
    path("quizzes/", QuizListView.as_view(), name="quiz-list"),
    path("quizzes/<uuid:pk>/", QuizDetailView.as_view(), name="quiz-detail"),
    path("answers/submit/", SubmitAnswerView.as_view(), name="submit-answer"),
    path("quizzes/<uuid:quiz_id>/submit/", SubmitQuizResultView.as_view(), name="submit-quiz-result"),
    path("quizzes/<uuid:quiz_id>/result/", QuizResultView.as_view(), name="quiz-result"),

    path("courses/", CourseViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name="course-list-create"),

    path("courses/<uuid:pk>/", CourseViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'delete': 'destroy'
    }), name="course-detail"),

    path("courses/enrollments/", EnrollmentViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name="enrollment-list-create"),

    path("courses/enrollments/<uuid:pk>/", EnrollmentViewSet.as_view({
        'get': 'retrieve',
        'delete': 'destroy'
    }), name="enrollment-detail"),
    path('courses/checkout/<uuid:course_id>/', CheckoutCourseSessionView.as_view(), name='checkout_course'),
    path('success/', SuccessfulCoursePaymentView.as_view(), name='payment_success'),

]

