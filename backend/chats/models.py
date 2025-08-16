import secrets
from django.db import models
from users.models import User
from django.utils import timezone


class Chat(models.Model):
    """
    represent a single conversation
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chats")
    unique_hex_id = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True,  # Allow NULL in database for existing records before migration
    )
    title = models.CharField(max_length=35, default="New Chat")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Chat"
        verbose_name_plural = "Chats"
        ordering = ["-updated_at"]

    def __str__(self):
        return (
            f"chat-id: {self.id} -> title: {self.title}, User: {self.user.telegram_id}"
        )

    def save(self, *args, **kwargs):
        # Overrides the default save method to generate a unique_hex_id
        # Check if the object is new (has no primary key yet)
        if not self.pk:
            while True:
                # Generate a 20-character hex string (10 bytes)
                new_hex_id = secrets.token_hex(10)
                # Check if this ID already exists in the database
                if not Chat.objects.filter(unique_hex_id=new_hex_id).exists():
                    self.unique_hex_id = new_hex_id
                    # Exit the loop once a unique ID is found
                    break
        super().save(*args, **kwargs)


class ChatContext(models.Model):
    """
    represent a context of an conversation/chat
    """

    chat = models.OneToOneField(
        Chat, on_delete=models.CASCADE, related_name="context", primary_key=True
    )

    # store context data
    context_data = models.TextField()

    class Meta:
        verbose_name = "Chat Context"
        verbose_name_plural = "Chat Contexts"

    def __str__(self):
        return f"Context for Chat ID: {self.chat.id}"


class Message(models.Model):
    """
    Represents a single message within a chat session.
    """

    # You might want to distinguish between your bot's direct responses and Gemini's
    CHAT_SENDER_CHOICES = [("user", "User"), ("model", "Gemini Model")]

    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages")
    sender = models.CharField(max_length=12, choices=CHAT_SENDER_CHOICES)
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "Message"
        verbose_name_plural = "Messages"
        ordering = ["-timestamp"]

    def __str__(self):
        return f"message-id: {self.id} -> chat: {self.chat.id} -> sender: {self.sender}"
