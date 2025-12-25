from django.urls import path
from . import views

urlpatterns = [
    path('messages/myMessages/<int:user_id>',views.MyInbox.as_view() ,name= "create-chat"),
    path('messages/<int:sender_id>/<int:receiver_id>/', views.getMessages.as_view(), name='get-messages'),
    path('sendMessages/',views.sendMessage.as_view() ,name= "send-messages"),
    path('mark-read/<int:sender_id>/', views.MarkMessagesRead.as_view(), name='mark-read'),
]