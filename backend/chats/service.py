import logging
from django.db import transaction
from django.http import JsonResponse
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404

from .models import Chat, Message, ChatContext
from .serializers import (
    ChatSerializer,
    ChatDetailSerializer,
    MessageInputSerializer,
    MessageSerializer,
)
from utils.ai import (
    generate_model_response,
    prepare_gemini_history,
    extract_json_from_model_response,
    generate_chat_title,
)


def user_chats(current_user):
    # Get all current_user chats, ordered by updated_at
    chats = Chat.objects.filter(user=current_user)

    # Serialize the queryset. 'many=True' indicates that we are serializing a list of objects.
    serializer = ChatSerializer(chats, many=True)
    return JsonResponse({"chat_list": serializer.data}, status=200)


def create_new_chat(data, current_user):
    # request.data contain optional 'title', JSON payload sent by the client.
    serializer = ChatSerializer(data=data)

    if serializer.is_valid():
        # This ensures the new chat is linked to the authenticated user.
        serializer.save(user=current_user)
        return JsonResponse({"new_chat": serializer.data}, status=201)
    else:
        logging.error(f"Failed to create new chat for user -> {current_user.username}")
        return JsonResponse({"error": "Something went wrong!"}, status=400)


def check_chat_permission(chat, current_user):
    """
    Checks if the current user is the owner of the chat.

    Returns:
        None if authorized, or a JsonResponse with a 403 status if unauthorized.
    """
    if chat.user != current_user:
        logging.error(
            f"Requested chat is not belong to current_user. username: {current_user}, chat_author: {chat.user}"
        )

        return JsonResponse(
            {"error": "Request chat is not belong to current_user"}, status=403
        )
    return None


def get_single_chat(current_user, unique_hex_id):
    if not (len(unique_hex_id) == 20 and unique_hex_id.isalnum()):
        return JsonResponse({"error": "Invalid conversation ID format."}, status=400)

    # load the chat
    chat = get_object_or_404(
        Chat.objects.select_related("user", "context").prefetch_related(
            Prefetch("messages", queryset=Message.objects.order_by("timestamp"))
        ),
        unique_hex_id=unique_hex_id,
    )

    permission = check_chat_permission(chat, current_user)
    if permission:
        return permission

    serializer = ChatDetailSerializer(chat)
    return JsonResponse({"single_chat": serializer.data}, status=200)


def delete_user_chat(current_user, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)

    permission = check_chat_permission(chat, current_user)
    if permission:
        return permission

    title = chat.title
    # delete the chat
    chat.delete()
    return JsonResponse({"title": title}, status=204)


def inbox(data, current_user):
    # validate request data
    serializer = MessageInputSerializer(data=data)
    if not serializer.is_valid():
        logging.error("Failed to validate chat json body")
        return JsonResponse(serializer.errors, status=400)

    validated_data = serializer.validated_data
    user_chat_id = validated_data["chat_id"]
    user_message_content = validated_data["content"]

    # load the chat
    try:
        chat = Chat.objects.select_related("user", "context").get(id=user_chat_id)
    except Chat.DoesNotExist:
        logging.warning(f"Chat not found for id: {user_chat_id}")
        return JsonResponse({"error": "Conversation not found."}, status=404)

    permission = check_chat_permission(chat, current_user)
    if permission:
        return permission

    try:
        # Use a database transaction to ensure atomicity
        # If any part of saving messages or getting LLM response fails,
        # all changes within this block are rolled back.
        with transaction.atomic():
            # create a new message for user
            user_message = Message.objects.create(
                chat=chat, sender="user", content=user_message_content
            )

            gemini_history = prepare_gemini_history(chat, user_message_content)
            gemini_response_data = generate_model_response(gemini_history)
            model_reply, new_context = extract_json_from_model_response(
                gemini_response_data
            )

            # create a new message for model
            model_message = Message.objects.create(
                chat=chat, sender="model", content=model_reply
            )

            # create/update context
            chat_context, created = ChatContext.objects.update_or_create(
                chat=chat, defaults={"context_data": new_context}
            )

            user_data = MessageSerializer(user_message).data
            model_data = MessageSerializer(model_message).data

            # if the title is default generate a title and return in response
            if chat.title == Chat.DEFAULT_TITLE:
                title = generate_chat_title(user_message_content, model_reply)
                chat.title = title
                chat.save()
                return JsonResponse(
                    {"title": title, "user": user_data, "model": model_data}, status=200
                )
            return JsonResponse({"user": user_data, "model": model_data}, status=200)
    except Exception as e:
        logging.error(f"Failed in chat new message. error: {str(e)}")
        return JsonResponse({"error": "Something went worng!"}, status=500)
