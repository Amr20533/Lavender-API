from rest_framework import serializers
from .models import Favorite
from account.models import Profile

class FavoriteSerializer(serializers.ModelSerializer):
    specialist_id = serializers.PrimaryKeyRelatedField(
        queryset=Profile.objects.all(), 
        source='specialist'
    )

    def validate_specialist(self, value):
        if value.role != 'SPECIALIST':
            raise serializers.ValidationError("This user is not a specialist.")
        return value

    class Meta:
        model = Favorite
        fields = ['id', 'specialist_id', 'user', 'in_favorite', 'created_at']
