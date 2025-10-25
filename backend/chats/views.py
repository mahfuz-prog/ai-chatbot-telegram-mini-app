from rest_framework.decorators import api_view
from utils.helper import check_tg_data_string

from . import service


# list all current_user chats
@api_view(["GET"])
@check_tg_data_string
def list_user_chat(request, current_user):
    return service.user_chats(current_user)


# create a new chat
@api_view(["POST"])
@check_tg_data_string
def new_chat(request, current_user):
    return service.create_new_chat(request.data, current_user)


# get a single conversation
@api_view(["GET"])
@check_tg_data_string
def single_chat(request, current_user, unique_hex_id):
    return service.get_single_chat(current_user, unique_hex_id)


# message with model
@api_view(["POST"])
@check_tg_data_string
def chatting(request, current_user):
    return service.inbox(request.data, current_user)


# delete a chat
@api_view(["DELETE"])
@check_tg_data_string
def delete_chat(request, current_user, chat_id):
    return service.delete_user_chat(current_user, chat_id)
