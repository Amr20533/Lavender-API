from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import Favorite, Review, CourseReview
from account.models import Profile, RoleChoices
from .serializers import FavoriteSerializer, ReviewSerializer, CourseReviewSerializer
from programs.models import Course

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_favorites(request):
    serializer = FavoriteSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        specialist = serializer.validated_data['specialist']
        favorite, created = Favorite.objects.get_or_create(
            user=request.user,
            specialist=specialist,
            defaults={'in_favorite': True}
        )

        if not created:
            if not favorite.in_favorite:
                favorite.in_favorite = True
                favorite.save()
                return Response({"status": "success", "message": "Added to favorites."}, status=status.HTTP_200_OK)
            return Response({"status": "info", "message": "Already in favorites."}, status=status.HTTP_200_OK)

        return Response({"status": "success", "message": "Added to favorites."}, status=status.HTTP_201_CREATED)

    return Response({"status": "error", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_favorites(request):
    favorites = Favorite.objects.filter(user=request.user, in_favorite=True)
    serializer = FavoriteSerializer(favorites, many=True)
    return Response({
        "status": "success",
        "favorites": serializer.data
    }, status=status.HTTP_200_OK)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_favorite(request, specialist_id):
    try:
        favorite = Favorite.objects.get(user=request.user, specialist_id=specialist_id)
        if not favorite.in_favorite:
            return Response({"status": "info", "message": "Already not in favorites."}, status=status.HTTP_200_OK)
        
        favorite.in_favorite = False
        favorite.save()

        return Response({"status": "success", "message": "Removed from favorites."}, status=status.HTTP_200_OK)
    except Favorite.DoesNotExist:
        return Response({"status": "error", "message": "Favorite not found."}, status=status.HTTP_404_NOT_FOUND)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_review(request):
    serializer = ReviewSerializer(data=request.data)

    if serializer.is_valid():
        try:
            specialist = serializer.validated_data['specialist']

            # Ensure target user is a specialist
            if specialist.role != RoleChoices.SPECIALIST:
                return Response({
                    "status": "error",
                    "message": "Target user is not a specialist."
                }, status=status.HTTP_400_BAD_REQUEST)

            # Ensure reviewer is a patient
            if request.user.profile.role != RoleChoices.PATIENT:
                return Response({
                    "status": "error",
                    "message": "Only patients can leave reviews."
                }, status=status.HTTP_403_FORBIDDEN)

        except Profile.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Specialist not found."
            }, status=status.HTTP_404_NOT_FOUND)

        review, created = Review.objects.update_or_create(
            user=request.user,
            specialist=specialist,
            defaults={
                'rating': serializer.validated_data['rating'],
                'comment': serializer.validated_data.get('comment', '')
            }
        )

        return Response({
            "status": "success",
            "message": "Review created." if created else "Review updated."
        }, status=status.HTTP_201_CREATED)

    return Response({
        "status": "error",
        "errors": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_reviews(request, specialist_id):
    try:
        specialist = Profile.objects.get(pk=specialist_id, role=RoleChoices.SPECIALIST)
    except Profile.DoesNotExist:
        return Response({
            "status": "error",
            "message": "Specialist not found."
        }, status=status.HTTP_404_NOT_FOUND)

    reviews = Review.objects.filter(specialist=specialist).select_related('user').order_by('-created_at')
    serializer = ReviewSerializer(reviews, many=True)
    return Response({
        "status": "success",
        "reviews": serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_review(request, specialist_id):
    try:
        review = Review.objects.get(user=request.user, specialist_id=specialist_id)
        review.delete()
        return Response({
            "status": "success",
            "message": "Review deleted."
        }, status=status.HTTP_200_OK)
    except Review.DoesNotExist:
        return Response({
            "status": "error",
            "message": "Review not found."
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_course_review(request):
    serializer = CourseReviewSerializer(data=request.data)
    if serializer.is_valid():
        profile = request.user.profile
        course = serializer.validated_data['course']

        # Prevent instructor from reviewing own course
        if course.instructor == profile:
            return Response({
                "status": "error",
                "message": "You cannot review your own course."
            }, status=status.HTTP_403_FORBIDDEN)

        review, created = CourseReview.objects.update_or_create(
            user=profile,
            course=course,
            defaults={
                'rating': serializer.validated_data['rating'],
                'comment': serializer.validated_data.get('comment', '')
            }
        )
        return Response({
            "status": "success",
            "message": "Review added." if created else "Review updated."
        }, status=status.HTTP_201_CREATED)

    return Response({"status": "error", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_course_reviews(request, course_id):
    try:
        course = Course.objects.get(pk=course_id)
    except Course.DoesNotExist:
        return Response({"status": "error", "message": "Course not found."}, status=status.HTTP_404_NOT_FOUND)

    reviews = course.reviews.select_related('user').order_by('-created_at')
    serializer = CourseReviewSerializer(reviews, many=True)
    return Response({"status": "success", "reviews": serializer.data}, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_course_review(request, course_id):
    try:
        review = CourseReview.objects.get(user=request.user.profile, course_id=course_id)
        review.delete()
        return Response({"status": "success", "message": "Review deleted."}, status=status.HTTP_200_OK)
    except CourseReview.DoesNotExist:
        return Response({"status": "error", "message": "Review not found."}, status=status.HTTP_404_NOT_FOUND)
