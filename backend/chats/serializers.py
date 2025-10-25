from rest_framework import serializers
from .models import Chat, Message


# serialize chat without messages
class ChatSerializer(serializers.ModelSerializer):
    """
    Serializer for the Chat model.
    """

    class Meta:
        model = Chat
        fields = ["id", "unique_hex_id", "title", "created_at", "updated_at"]
        read_only_fields = ["id", "unique_hex_id", "created_at", "updated_at"]


# serialize messages
class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for the Message model.
    Used for nested representation within ChatSerializer.
    """

    class Meta:
        model = Message
        fields = ["id", "sender", "content", "timestamp"]
        read_only_fields = ["id", "timestamp"]


# serialize chat with messages
class ChatDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for the Chat model, designed for detail views.
    Includes nested messages (ordered by timestamp) and chat context.
    """

    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Chat
        fields = [
            "id",
            "unique_hex_id",
            "title",
            "created_at",
            "updated_at",
            "messages",
        ]
        read_only_fields = [
            "id",
            "unique_hex_id",
            "created_at",
            "updated_at",
            "messages",
        ]


class MessageInputSerializer(serializers.Serializer):
    chat_id = serializers.IntegerField(max_value=999999)
    content = serializers.CharField(max_length=250, min_length=1)
