from rest_framework import generics
from rest_framework.parsers import MultiPartParser, FormParser
from .models import MusicCard, PsychoMeasurementQuiz, UserAnswer, QuizResult, QuizResultCategory
from .serializers import *
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

class MusicCardListCreateView(generics.ListCreateAPIView):
    queryset = MusicCard.objects.all()
    serializer_class = MusicCardSerializer
    parser_classes = (MultiPartParser, FormParser)

class MusicCardDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MusicCard.objects.all()
    serializer_class = MusicCardSerializer
    parser_classes = (MultiPartParser, FormParser)
    lookup_field = "id"

class QuizListView(generics.ListAPIView):
    queryset = PsychoMeasurementQuiz.objects.all().prefetch_related("questions__answers")
    serializer_class = PsychoMeasurementQuizSerializer


class QuizDetailView(generics.RetrieveAPIView):
    queryset = PsychoMeasurementQuiz.objects.all().prefetch_related("questions__answers")
    serializer_class = PsychoMeasurementQuizSerializer


# ---------------- ANSWERS ---------------- #

class SubmitAnswerView(generics.CreateAPIView):
    serializer_class = UserAnswerSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        question = serializer.validated_data["question"]
        answer = serializer.validated_data["answer"]

        # بدل create → update_or_create
        user_answer, _ = UserAnswer.objects.update_or_create(
            user=user,
            question=question,
            defaults={"answer": answer}
        )

        # ----------------- تحديث النتيجة -----------------
        quiz = question.quiz
        user_answers = UserAnswer.objects.filter(
            user=user, question__quiz=quiz
        ).select_related("answer")

        total_score = sum(a.answer.score for a in user_answers)
        max_score = sum(
            q.answers.order_by("-score").first().score if q.answers.exists() else 0
            for q in quiz.questions.all()
        )

        result = None
        if max_score > 0:
            percentage = (total_score / max_score) * 100
            category = QuizResultCategory.objects.filter(
                quiz=quiz, min_score__lte=total_score, max_score__gte=total_score
            ).first()
            if category:
                result, _ = QuizResult.objects.update_or_create(
                    quiz=quiz,
                    user=user,
                    defaults={
                        "total_score": total_score,
                        "percentage": percentage,
                        "title": category.title,
                        "description": category.description,
                    },
                )
        return user_answer, result

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        answer, result = self.perform_create(serializer)

        response_data = {
            "answer": UserAnswerSerializer(answer).data,
            "result": QuizResultSerializer(result).data if result else None
        }
        return Response(response_data, status=status.HTTP_201_CREATED)

# ---------------- RESULTS ---------------- #

class SubmitQuizResultView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = QuizResultSerializer

    def post(self, request, quiz_id):
        quiz = get_object_or_404(PsychoMeasurementQuiz, id=quiz_id)
        user = request.user

        # Fetch user answers for this quiz
        user_answers = UserAnswer.objects.filter(user=user, question__quiz=quiz).select_related("answer")

        if not user_answers.exists():
            return Response(
                {"error": "You haven't answered this quiz yet."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Calculate total score
        total_score = sum(a.answer.score for a in user_answers)

        # Get maximum possible score dynamically
        max_score = sum(
            q.answers.order_by("-score").first().score if q.answers.exists() else 0
            for q in quiz.questions.all()
        )

        if max_score == 0:
            return Response(
                {"error": "This quiz is not configured with valid answers."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        percentage = (total_score / max_score) * 100

        # Find matching result category
        category = QuizResultCategory.objects.filter(
            quiz=quiz, min_score__lte=total_score, max_score__gte=total_score
        ).first()

        if not category:
            return Response(
                {"error": f"No result category matches score {total_score}."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Save or update result
        result, created = QuizResult.objects.update_or_create(
            quiz=quiz,
            user=user,
            defaults={
                "total_score": total_score,
                "percentage": percentage,
                "title": category.title,
                "description": category.description,
            },
        )

        serializer = self.get_serializer(result)
        return Response(serializer.data, status=status.HTTP_200_OK)


class QuizResultView(generics.RetrieveAPIView):
    serializer_class = QuizResultSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        quiz_id = self.kwargs["quiz_id"]
        return get_object_or_404(
            QuizResult,
            quiz__id=quiz_id,
            user=self.request.user
        )
