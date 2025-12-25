from rest_framework import generics
from rest_framework.parsers import MultiPartParser, FormParser
from .models import *
from .serializers import *
from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
import stripe
from django.conf import settings  
from django.views.generic import TemplateView
from rest_framework.views import APIView
from decimal import Decimal, InvalidOperation
from account.models import RoleChoices

stripe.api_key = settings.STRIPE_SECRET_KEY

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



class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all().order_by('-created_at')
    serializer_class = CourseSerializer

    def get_permissions(self):
        # Allow everyone to view courses and details
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        # Require auth for actions like create/update/destroy and access
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        user = self.request.user
        profile = user.profile

        if profile.role != RoleChoices.SPECIALIST:
            raise serializers.ValidationError("Only specialists can create courses.")

        serializer.save(instructor=profile)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def access(self, request, pk=None):
        """
        Return full access to course content (videos, materials)
        only if user has paid enrollment.
        """
        course = self.get_object()
        profile = request.user.profile

        has_access = Enrollment.objects.filter(
            user=profile,
            course=course,
            is_paid=True
        ).exists()

        if has_access:
            # Use a more detailed serializer for full content
            data = CourseDetailSerializer(course, context={'request': request}).data
            return Response({"status": "success", "data": data})

        return Response(
            {"detail": "Course locked. Please complete payment to view videos."},
            status=403
        )


class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Enrollment.objects.filter(user=self.request.user.profile)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user.profile)



class SuccessfulCoursePaymentView(TemplateView):
    permission_classes = [AllowAny]
    template_name = 'index.html'
    
class CheckoutCourseSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, course_id):
        try:
            # ✅ 1. Get the course to pay for
            course = Course.objects.get(id=course_id)

            MAX_STRIPE_AMOUNT = Decimal("999999.99")
            quantity = int(request.data.get("quantity", 1))
            if quantity <= 0:
                return Response({"error": "Quantity must be positive."}, status=400)

            # ✅ 2. Convert and validate price
            try:
                price_str = str(course.price).strip()
                course_price = Decimal(price_str.replace(",", ""))
                total_price = course_price * quantity
                if total_price > MAX_STRIPE_AMOUNT:
                    total_price = MAX_STRIPE_AMOUNT
                    quantity = 1
            except (InvalidOperation, ValueError, TypeError):
                return Response({"error": "Invalid price format."}, status=400)

            # ✅ 3. Stripe Line Items
            line_items = [{
                "price_data": {
                    "currency": "usd",
                    "unit_amount": int(total_price * 100),  # Stripe expects cents
                    "product_data": {
                        "name": f"Course: {course.title}",
                        "description": f"Instructor: {course.instructor.user.get_full_name()}",
                    },
                },
                "quantity": quantity,
            }]

            # ✅ 4. Metadata to identify user & course
            session_metadata = {
                "course_id": str(course.id),
                "user_id": str(request.user.id)
            }

            # ✅ 5. Create Stripe Checkout Session
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=line_items,
                mode="payment",
                metadata=session_metadata,
                success_url=settings.SITE_URL + "api/v1/payment/success/",
                cancel_url=settings.SITE_URL + "api/v1/payment/cancel/"
            )

            # ✅ 6. Create Enrollment record (pending)
            enrollment, created = Enrollment.objects.get_or_create(
                user=request.user.profile,
                course=course,
                defaults={'is_paid': False}
            )

            # Save payment reference
            enrollment.payment_reference = checkout_session.id
            enrollment.save()

            return Response({
                "status": "success",
                "url": checkout_session.url
            }, status=200)

        except Course.DoesNotExist:
            return Response({"error": "Course not found."}, status=404)
        except stripe.error.StripeError as e:
            return Response({"error": f"Stripe error: {str(e)}"}, status=400)
        except Exception as e:
            return Response({"error": str(e)}, status=500)



class FreeProgramListView(generics.ListAPIView):
    permission_classes = (AllowAny, )
    queryset = FreeProgram.objects.all().order_by('-created_at')
    serializer_class = FreeProgramSerializer