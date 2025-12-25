from rest_framework import serializers
from .models import *
from account.serializers import UserSerializer

class MessageSerializer(serializers.ModelSerializer):
    receiver_profile = serializers.SerializerMethodField(read_only=True)
    sender_profile = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ChatBubble
        fields = (
            'id', 
            'sender', 
            'receiver', 
            'receiver_profile', 
            'sender_profile', 
            'message', 
            'is_read', 
            'timestamp'
        )

    def get_receiver_profile(self, obj):
        serializer = UserSerializer(obj.receiver, context=self.context)
        return serializer.data

    def get_sender_profile(self, obj):
        serializer = UserSerializer(obj.sender, context=self.context)
        return serializer.data
    

class ReadReceiptSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)  
    read_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = ReadReceipt
        fields = ('id', 'message', 'user', 'read_at')
