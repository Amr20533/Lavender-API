from .serializers import *
from .models import *
from rest_framework.response import Response
from django.db.models import Subquery, OuterRef, Q
from rest_framework import generics,status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

class MyInbox(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer

    def get_queryset(self):
        user_id = self.kwargs['user_id']

        # 1. Subquery to find the latest message ID for each conversation
        last_msg_subquery = ChatBubble.objects.filter(
            Q(sender=OuterRef('id'), receiver=user_id) | 
            Q(receiver=OuterRef('id'), sender=user_id)
        ).order_by('-id')[:1] 

        # 2. Get the actual message objects
        messages = ChatBubble.objects.filter(
            id__in=Subquery(
                User.objects.filter(
                    Q(sender__receiver=user_id) |
                    Q(receiver__sender=user_id)
                ).distinct().annotate(
                    last_msg=Subquery(last_msg_subquery.values('id')) 
                ).values('last_msg') 
            )
        ).order_by('-id')

        # 3. Mark received messages as read
        # Note: Be careful with .save() inside get_queryset as it triggers 
        # database writes during a GET request.
        for message in messages:
            if message.receiver.id == int(user_id):
                message.is_read = True 
                message.save() 

        return messages

    # OVERRIDE the list method to change response structure
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)

        
class getMessages(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer

    def get_queryset(self):
        sender_id = self.kwargs['sender_id']
        receiver_id = self.kwargs['receiver_id']
        return ChatBubble.objects.filter(
            Q(sender_id=sender_id, receiver_id=receiver_id) |
            Q(sender_id=receiver_id, receiver_id=sender_id)
        ).order_by('timestamp')

    def list(self, request, *args, **kwargs):
        sender_id = self.kwargs['sender_id']
        receiver_id = self.kwargs['receiver_id']

        # Logic: If I am receiving these messages, mark them as read
        ChatBubble.objects.filter(
            sender_id=sender_id, 
            receiver_id=receiver_id, 
            is_read=False
        ).update(is_read=True)

        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({"messages": serializer.data})


class sendMessage(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]  
    serializer_class = MessageSerializer
    
    def perform_create(self, serializer):
        serializer.save(sender = self.request.user)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data = request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MarkMessagesRead(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, sender_id):
        # We want to mark messages sent BY sender_id TO the current user
        unread_messages = ChatBubble.objects.filter(
            sender_id=sender_id, 
            receiver=request.user, 
            is_read=False
        )
        
        # .update() is much faster than a for-loop with .save()
        count = unread_messages.update(is_read=True)
        
        return Response(
            {"message": f"{count} messages marked as read."}, 
            status=status.HTTP_200_OK
        )