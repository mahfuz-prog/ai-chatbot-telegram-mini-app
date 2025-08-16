from rest_framework.decorators import api_view
from django.http import JsonResponse
from utils.helper import check_tg_data_string


@api_view(["GET"])
@check_tg_data_string
def get_user(request, current_user):
	return JsonResponse({}, status=200)