from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Favorite
from account.models import Profile
from .serializers import FavoriteSerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_favorites(request):
    serializer = FavoriteSerializer(data=request.data)
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
