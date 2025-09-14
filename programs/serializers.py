from rest_framework import serializers
from .models import (
    MusicCard,
    PsychoMeasurementQuiz,
    QuizQuestion,
    QuizAnswer,
    UserAnswer,
    QuizResultCategory,
    QuizResult,
)

class MusicCardSerializer(serializers.ModelSerializer):
    duration = serializers.DurationField(read_only=True)
    album_cover = serializers.ImageField(required=False, allow_null=True)
    audio_file = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = MusicCard
        fields = "__all__"

# ---------------- QUIZ STRUCTURE ---------------- #

class QuizAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizAnswer
        fields = ["id", "text", "score"]


class QuizQuestionSerializer(serializers.ModelSerializer):
    answers = QuizAnswerSerializer(many=True, read_only=True)

    class Meta:
        model = QuizQuestion
        fields = ["id", "text", "order", "answers"]


class PsychoMeasurementQuizSerializer(serializers.ModelSerializer):
    questions = QuizQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = PsychoMeasurementQuiz
        fields = ["id", "title", "image", "created_at", "questions"]


# ---------------- USER ANSWERS ---------------- #

class UserAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAnswer
        fields = ["id", "question", "answer"]
        read_only_fields = ["id"]

    # def create(self, validated_data):
    #     user = self.context["request"].user
    #     return UserAnswer.objects.create(user=user, **validated_data)


# ---------------- RESULT CATEGORIES ---------------- #

class QuizResultCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizResultCategory
        fields = ["id", "min_score", "max_score", "title", "description"]


# ---------------- FINAL RESULT ---------------- #

class QuizResultSerializer(serializers.ModelSerializer):
    quiz = serializers.StringRelatedField(read_only=True)
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = QuizResult
        fields = [
            "id",
            "quiz",
            "user",
            "total_score",
            "percentage",
            "title",
            "description",
            "created_at",
        ]
