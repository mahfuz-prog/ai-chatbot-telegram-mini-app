import logging
from django.db import transaction
from django.http import JsonResponse
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404

from utils.ai import WeatherInformationPipeline
from utils.helper import extract_data_from_model_response
from .models import Chat, Message, ChatContext
from .serializers import (
    ChatSerializer,
    ChatDetailSerializer,
    MessageInputSerializer,
    MessageSerializer,
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
        # new chat -> linked to the authenticated user. crate context for chat
        chat = serializer.save(user=current_user)
        _ = ChatContext.objects.create(chat=chat, context_data="no context availabl")
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
    """
    Handle incoming user messages, process through pipeline,
    and return both user and model responses in JSON.
    """

    # Validate request data
    serializer = MessageInputSerializer(data=data)
    if not serializer.is_valid():
        logging.error("Invalid chat request payload")
        return JsonResponse(serializer.errors, status=400)

    validated = serializer.validated_data
    chat_id = validated["chat_id"]
    user_input = validated["content"]

    try:
        chat = Chat.objects.select_related("user", "context").get(id=chat_id)
    except Chat.DoesNotExist:
        logging.warning(f"Chat not found for id: {chat_id}")
        return JsonResponse({"error": "Conversation not found."}, status=404)

    # Verify permissions
    permission = check_chat_permission(chat, current_user)
    if permission:
        return permission

    # instantiate the agentic pipeline
    pipeline = WeatherInformationPipeline()

    try:
        context_data = chat.context.context_data
        response = pipeline.chat(user_input, context_data)
        model_reply, new_context = extract_data_from_model_response(response)

        # check title
        generated_title = None
        if chat.title == Chat.DEFAULT_TITLE:
            generated_title = pipeline.generate_title(user_input, model_reply)

        # Atomic DB writes
        with transaction.atomic():
            user_msg = Message.objects.create(
                chat=chat, sender="user", content=user_input
            )

            model_msg = Message.objects.create(
                chat=chat, sender="model", content=model_reply
            )

            _ = ChatContext.objects.filter(chat=chat).update(context_data=new_context)

            # save title if generated
            if generated_title:
                chat.title = generated_title
                chat.save(update_fields=["title"])

        user_data = MessageSerializer(user_msg).data
        model_data = MessageSerializer(model_msg).data

        response_data = {"user": user_data, "model": model_data}
        if generated_title:
            response_data["title"] = generated_title

        return JsonResponse(response_data, status=200)

    except Exception as e:
        logging.error(f"Chat message processing failed. error: {str(e)}")
        return JsonResponse({"error": "Something went wrong!"}, status=500)
