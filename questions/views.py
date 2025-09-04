from .models import IntroAnswer
from .serializers import *
from rest_framework import mixins, viewsets
from rest_framework.response import Response


class IntroQuestionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = IntroQuestion.objects.all()
    serializer_class = IntroQuestionSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({"data": serializer.data})

# class IntroAnswerViewSet(viewsets.ModelViewSet):
#     queryset = IntroAnswer.objects.all()
#     serializer_class = IntroAnswerSerializer

#     def perform_create(self, serializer):
#         serializer.save(user=self.request.user)

class SubmitAnswerViewSet(mixins.CreateModelMixin,
                          mixins.ListModelMixin,
                          viewsets.GenericViewSet):
    queryset = IntroAnswer.objects.all()
    serializer_class = IntroAnswerSerializer

    def get_queryset(self):
        # Only return answers from the logged-in user
        return IntroAnswer.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

