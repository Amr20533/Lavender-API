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
    Enrollment,
    ProgramSession,
    SessionItem,
    FreeProgram
)
from account.serializers import ProfileSerializer
from account.models import RoleChoices

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
    instructor = ProfileSerializer(read_only=True)
    # reviews = CourseReviewSerializer(many=True, read_only=True)
    avg_rating = serializers.FloatField(read_only=True)  # ⬅️ added

    class Meta:
        model = Course
        fields = [
            'id',
            'title',
            'description',
            'image',
            'price',
            'category',
            'duration',
            'instructor',
            'total_sessions',
            'avg_rating',
            # 'reviews',
            'videos',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'total_sessions']

    def perform_create(self, serializer):
        user = self.context['request'].user
        profile = user.profile

        if profile.role != RoleChoices.SPECIALIST:
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

class SessionItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionItem
        fields = [ 'name', 'description']

class ProgramSessionSerializer(serializers.ModelSerializer):
    items = SessionItemSerializer(many=True, read_only=True)
    formatted_date = serializers.ReadOnlyField(source='get_formatted_date')
    video_url = serializers.SerializerMethodField()

    class Meta:
        model = ProgramSession
        fields = ['id', 'title', 'status', 'video', 'video_url', 'duration', 'formatted_date', 'items']

    def get_video_url(self, obj):
        if obj.video:
            return obj.video.url
        return None

# 4. Main Free Program Serializer
class FreeProgramSerializer(serializers.ModelSerializer):
    author = ProfileSerializer(source='user.profile', read_only=True)
    category = serializers.ReadOnlyField(source='category.title')
    sessions = ProgramSessionSerializer(many=True, read_only=True)

    next_session_date = serializers.SerializerMethodField()
    next_session_title = serializers.SerializerMethodField()
    # is_live = serializers.SerializerMethodField()

    class Meta:
        model = FreeProgram
        fields = [
            'id',
            'author',
            'category',
            'title',
            'image',
            'viewers_number',
            'sessions',
            'next_session_date',
            'next_session_title',
            # 'is_live',
        ]

    # 🔥 LIVE first, then UPCOMING
    def _get_priority_session(self, obj):
        live = obj.sessions.filter(status='جارية الان').first()
        if live:
            return live

        upcoming = obj.sessions.filter(status='قادمة') \
            .order_by('appointment_date') \
            .first()
        return upcoming

    def get_next_session_title(self, obj):
        session = self._get_priority_session(obj)
        return session.title if session else "لا توجد جلسات قادمة"

    def get_next_session_date(self, obj):
        session = self._get_priority_session(obj)
        return session.get_formatted_date() if session else None

    def get_is_live(self, obj):
        return obj.sessions.filter(status='جارية الان').exists()
