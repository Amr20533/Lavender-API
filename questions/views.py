from rest_framework import viewsets
from .models import IntroAnswer
from .serializers import IntroAnswerSerializer

class IntroAnswerViewSet(viewsets.ModelViewSet):
    queryset = IntroAnswer.objects.all()
    serializer_class = IntroAnswerSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        
