from rest_framework import serializers
from .models import (
    MusicCard,
    PsychoMeasurementQuiz,
    QuizQuestion,
    QuizAnswer,
    UserAnswer,
    QuizResultCategory,
    QuizResult,
    Course,
    CourseVideo,
    Enrollment
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


class CourseVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseVideo
        fields = ['id', 'title', 'video_url', 'order']


class CourseSerializer(serializers.ModelSerializer):
    videos = CourseVideoSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'image', 'price', 'category', 'duration', 'total_sessions', 'videos', 'created_at']
        read_only_fields = ['id', 'created_at', 'total_sessions']

    def perform_create(self, serializer):
        user = self.request.user
        profile = user.profile

        if profile.role != 'SPECIALIST':
            from rest_framework import serializers
            raise serializers.ValidationError("Only specialists can create courses.")

        serializer.save(instructor=profile)



class EnrollmentSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    course_id = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(),
        source='course',
        write_only=True
    )

    class Meta:
        model = Enrollment
        fields = ['id', 'course', 'course_id', 'is_paid', 'enrolled_at']
