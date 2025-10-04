from rest_framework import serializers
from .models import Favorite, Review
from account.models import Profile

class FavoriteSerializer(serializers.ModelSerializer):
    specialist_id = serializers.PrimaryKeyRelatedField(
    queryset=Profile.objects.filter(role='SPECIALIST'),
    source='specialist'
)


    def validate_specialist(self, value):
        if getattr(value, 'role', None) != 'SPECIALIST':
            raise serializers.ValidationError("This user is not a specialist.")
        return value

    class Meta:
        model = Favorite
        fields = ['id', 'specialist_id', 'user', 'in_favorite', 'created_at']

class ReviewSerializer(serializers.ModelSerializer):
    specialist = serializers.PrimaryKeyRelatedField(queryset=Profile.objects.all())

    class Meta:
        model = Review
        fields = ['user','specialist', 'rating', 'comment', 'created_at']
        read_only_fields = ['user', 'created_at']

    def validate_rating(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value

