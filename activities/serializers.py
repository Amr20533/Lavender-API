from rest_framework import serializers
from .models import Favorite, Review
from account.models import Profile

class FavoriteSerializer(serializers.ModelSerializer):
    specialist_id = serializers.PrimaryKeyRelatedField(
        queryset=Profile.objects.all(),
        source='specialist'
    )

    class Meta:
        model = Favorite
        fields = ['id', 'specialist_id', 'in_favorite', 'created_at']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)


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

