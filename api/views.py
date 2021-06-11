from api.errors import error_response, ErrorEnum
from django.conf import settings
from twilio.rest import Client
from typing import Union
import secrets
from rest_framework import status
from api.models import UserInfo
from rest_framework.decorators import api_view
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.core.exceptions import ObjectDoesNotExist
from django.db import DatabaseError
from django.contrib.auth.hashers import check_password, make_password


@api_view(["POST"])
@csrf_exempt
def login(request) -> Union[HttpResponse, JsonResponse]:
    """
    Logs a user in
    :param request: POST request
    :return: info about the user's account and a token for their current session,
      or an error if their account couldn't be found
    """
    body = json.loads(request.body.decode('utf-8'))
    try:
        user = UserInfo.objects.get(email=body['email'])
    except ObjectDoesNotExist as e:
        # Username/password don't match anything in the database
        return error_response(ErrorEnum.UNRECOGNIZED_LOGIN_INFO, http_status=status.HTTP_401_UNAUTHORIZED)

    is_correct_password = check_password(body['password'], user.password)
    if is_correct_password:
        return JsonResponse({
            'token': 'a234klqj2f3',
            'user': {
                "userId": user.id,
                "email": user.email,
                "name": user.first_name + " " + user.last_name}  # todo
        }, safe=False, status=status.HTTP_200_OK)
    else:
        return error_response(ErrorEnum.UNRECOGNIZED_LOGIN_INFO, http_status=status.HTTP_401_UNAUTHORIZED)


@api_view(["POST"])
@csrf_exempt
def signup(request) -> Union[HttpResponse, JsonResponse]:
    """
    Creates a new user account
    :param request: POST request
    :return: info about the new user's account as well as a token for their session, or an error
      if something went wrong
    """
    body = json.loads(request.body.decode('utf-8'))
    if email_exists(body["email"]):
        return HttpResponse("Username already in use", status=status.HTTP_409_CONFLICT)

    raw_password = body["password"]
    hashed_password = make_password(raw_password)
    # todo name is split dup
    # todo we should move passwords out of this table
    try:
        new_user = UserInfo.objects.create(first_name=body["name"], email=body["email"], password=hashed_password)
    except DatabaseError as e:
        return error_response(ErrorEnum.EMAIL_ALREADY_REGISTERED, http_status=status.HTTP_409_CONFLICT)

    return JsonResponse({
        'token': 'mocktoken',
        'user': {
            "userId": new_user.id,
            "email": new_user.email,
            "name": new_user.first_name + " " + new_user.last_name}
    }, safe=False, status=status.HTTP_200_OK)


# Sends out the emergency message to user's emergency contacts.
def _send_twilio_sms(message: str, userContactNumbers):
    # TODO: get user name and userContact numbers
    client = Client(secrets.TWILIO_ACCOUNT_SID, secrets.TWILIO_AUTH_TOKEN)
    for recipient in userContactNumbers:
        if recipient:
            client.messages.create(to=recipient, from_=settings.TWILIO_NUMBER, body=message)

    return HttpResponse("messages sent", 200)


def email_exists(email):
    return UserInfo.objects.filter(email=email).exists()
