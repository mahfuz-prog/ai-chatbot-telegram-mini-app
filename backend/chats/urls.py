from django.urls import path
from . import views

urlpatterns = [
    path('chat-list/', views.list_user_chat),
    path('new-chat/', views.new_chat),
    path('delete-chat/<int:chat_id>/', views.delete_chat),
    path('single-chat/<str:unique_hex_id>/', views.single_chat),
    path('chatting/', views.chatting),
]