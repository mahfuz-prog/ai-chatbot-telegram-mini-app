from django.contrib import admin
from .models import Chat, ChatContext, Message

admin.site.register(Chat)
admin.site.register(ChatContext)
admin.site.register(Message)