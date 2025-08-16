import json
from django.db import transaction
from django.http import JsonResponse
from .models import Chat, Message, ChatContext
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from .serializers import ChatSerializer, ChatDetailSerializer
from utils.helper import check_tg_data_string, generate_model_response
from django.db.models import Prefetch


# list all current_user chats
@api_view(["GET"])
@check_tg_data_string
def list_user_chat(request, current_user):
    # Get all chats associated with the current_user, ordered by updated_at
    chats = Chat.objects.filter(user=current_user)

    # Serialize the queryset. 'many=True' indicates that we are serializing a list of objects.
    serializer = ChatSerializer(chats, many=True)
    return JsonResponse({"chat_list": serializer.data}, status=200)


# create a new chat
@api_view(["POST"])
@check_tg_data_string
def new_chat(request, current_user):
    # request.data contain optional 'title', JSON payload sent by the client.
    serializer = ChatSerializer(data=request.data)

    if serializer.is_valid():
        # This ensures the new chat is linked to the authenticated user.
        chat = serializer.save(user=current_user)
        return JsonResponse({"new_chat": serializer.data}, status=201)
    return JsonResponse({"error": "Something went wrong!"}, status=400)


# get a single conversation
@api_view(["GET"])
@check_tg_data_string
def single_chat(request, current_user, unique_hex_id):
    # load the chat
    chat = get_object_or_404(
        Chat.objects.select_related("user", "context").prefetch_related(
            Prefetch("messages", queryset=Message.objects.order_by("timestamp"))
        ),
        unique_hex_id=unique_hex_id,
    )

    # check the chat belong from current_user
    if chat.user != current_user:
        return JsonResponse(
            {"error": "You do not have permission to read this chat."}, status=403
        )

    serializer = ChatDetailSerializer(chat)
    return JsonResponse({"single_chat": serializer.data}, status=200)


# message with model
@api_view(["POST"])
@check_tg_data_string
def chatting(request, current_user):
    user_chat_id = request.data.get("chat_id")
    user_message_content = request.data.get("content")

    # empty json
    if not user_message_content or not user_chat_id:
        return JsonResponse({"error": "Invalid json body!"}, status=400)

    # length check
    if len(str(user_chat_id)) > 6 or len(user_message_content) > 250:
        return JsonResponse({"error": "Invalid json body!"}, status=400)

    # load the chat
    chat = Chat.objects.select_related("user", "context").get(id=user_chat_id)

    # check if the chat belong to current user
    if chat.user != current_user:
        return JsonResponse(
            {"error": "You do not have permission to continue."}, status=403
        )

    try:
        # Use a database transaction to ensure atomicity
        # If any part of saving messages or getting LLM response fails,
        # all changes within this block are rolled back.
        with transaction.atomic():
            # if the title is default
            if chat.title == "New Chat":
                chat.title = user_message_content[:35]
                chat.save()

            # save user message
            user_message = Message.objects.create(
                chat=chat, sender="user", content=user_message_content
            )

            # The history should alternate between 'user' and 'model' roles.
            gemini_history = []

            # If there's an existing context, add it to the history
            if hasattr(chat, "context") and chat.context.context_data:
                context_data = chat.context.context_data
                gemini_history.append(
                    {
                        "role": "user",
                        "parts": [{"text": f"Previous context: {context_data}"}],
                    }
                )
                gemini_history.append(
                    {
                        "role": "model",
                        "parts": [{"text": "Acknowledged. I will use this context."}],
                    }
                )

            # Add the current user's message to the history
            gemini_history.append(
                {"role": "user", "parts": [{"text": user_message_content}]}
            )

            """
			generate a response. reply look like

				```json
					{
						"reply": "",
						"context_summary": ""
					}
				```
			"""
            gemini_response_data = generate_model_response(gemini_history)
            response_content = json.loads(gemini_response_data[7:-3])
            model_reply = response_content["reply"]
            new_context = response_content["context_summary"]

            # create a new message
            model_message = Message.objects.create(
                chat=chat, sender="model", content=model_reply
            )

            # Update context
            chat_context, created = ChatContext.objects.update_or_create(
                chat=chat, defaults={"context_data": new_context}
            )

            user = {
                "id": user_message.id,
                "sender": "user",
                "content": user_message.content,
                "timestamp": user_message.timestamp,
            }

            model = {
                "id": model_message.id,
                "sender": "model",
                "content": model_message.content,
                "timestamp": model_message.timestamp,
            }
            return JsonResponse({"user": user, "model": model}, status=200)
    except:
        return JsonResponse({"error": "Something went worng!"}, status=500)
    return JsonResponse({"error": "Something went worng!"}, status=500)


# delete a chat
@api_view(["DELETE"])
@check_tg_data_string
def delete_chat(request, current_user, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)

    # check if the chat belong to current user
    if chat.user != current_user:
        return JsonResponse(
            {"error": "You do not have permission to delete this chat."}, status=403
        )

    # delete the chat
    chat.delete()
    return JsonResponse({}, status=204)
