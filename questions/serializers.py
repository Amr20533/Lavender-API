from rest_framework import serializers
from .models import IntroQuestion, IntroOption, IntroAnswer

class IntroOptionSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = IntroOption
        fields = ['id', 'text', 'parentQuestions', 'children'] 
        
    def get_children(self, obj):
        return IntroOptionSerializer(obj.children.all(), many=True).data


class IntroQuestionSerializer(serializers.ModelSerializer):
    options = IntroOptionSerializer(many=True, read_only=True)

    class Meta:
        model = IntroQuestion
        fields = ['id', 'question', 'type', 'description', 'options']
        
class IntroAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntroAnswer
        fields = ['id', 'user', 'question', 'text_answer', 'selected_options', 'created_at']


# class IntroQuestionSerializer(serializers.ModelSerializer):
#     options = IntroOptionSerializer(many=True, required=False)

#     class Meta:
#         model = IntroQuestion
#         fields = ['id', 'question', 'type', 'description', 'options']

#     def create(self, validated_data):
#         options_data = validated_data.pop('options', [])
#         question = IntroQuestion.objects.create(**validated_data)
#         for option_data in options_data:
#             IntroOption.objects.create(question=question, **option_data)
#         return question

#     def update(self, instance, validated_data):
#         options_data = validated_data.pop('options', None)
#         for attr, value in validated_data.items():
#             setattr(instance, attr, value)
#         instance.save()

#         if options_data is not None:
#             instance.options.all().delete()
#             for option_data in options_data:
#                 IntroOption.objects.create(question=instance, **option_data)

#         return instance
