from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt

from api.errors import error_response, ErrorEnum
from api.models import UserContact, UserInfo
from django.http import JsonResponse
import json
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from twilio.rest import Client
import klip_secrets


# formats the emergency message
def _format_message(payload) -> str:
    """
        Formats the emergency message
        :param message: unformatted message
        :return: formatted message
    """
    location_url = "https://www.google.com/maps/place/" + payload["latitude"] + "," + payload["longitude"]
    return "Your friend may be in danger and is located at " + location_url


# handles the emergency request and sends emergency message user's contacts
@api_view(["POST"])
@csrf_exempt
def handle_emergency_request(request):
    """
        handles the emergency request and sends emergency message user's contacts
        :param request: a POST request
        :return: Message informing the user about whether their alert was successfully sent or not
    """
    payload = json.loads(request.body)
    userId = payload["userId"]

    if not UserInfo.objects.filter(id=payload["userId"]).exists():
        return error_response(ErrorEnum.USER_NOT_FOUND, http_status=status.HTTP_404_NOT_FOUND)

    responseMessageStrings = []

    # we may want to split this off into its own method
    try:
        phoneNumbers = map(lambda u: u.phoneNumber, UserContact.objects.filter(userId=userId))
    except ObjectDoesNotExist:
        return error_response(ErrorEnum.NO_USER_CONTACTS, http_status=status.HTTP_404_NOT_FOUND)

    # TODO throw exception if there are not any user contacts
    if not phoneNumbers:
        return error_response(ErrorEnum.NO_USER_CONTACTS, http_status=status.HTTP_404_NOT_FOUND)
    message = _format_message(payload)
    _send_twilio_sms(message, phoneNumbers)
    responseMessageStrings.append("We alerted all of your emergency contacts.")

    police_contacted = False

    # contact police if necessary

    # todo consider adding separate fields for if police or contacts have been alerted
    if police_contacted:
        responseMessageStrings.append("The police have been alerted.")
    else:
        responseMessageStrings.append("The police have NOT been alerted.")

    responseMessageStrings.append("Stay safe!")

    return JsonResponse({'response': ' '.join(responseMessageStrings)}, safe=False, status=status.HTTP_200_OK)

    """ In case of failure
    return JsonResponse({'response': 'WARNING: Something went wrong and we couldn\'t send out an alert. Stay safe!'}, safe=False, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    """


# Sends out the emergency message to user's emergency contacts.
def _send_twilio_sms(message: str, userContactNumbers):
    # TODO: get user name and userContact numbers
    client = Client(klip_secrets.TWILIO_ACCOUNT_SID, klip_secrets.TWILIO_AUTH_TOKEN)
    for recipient in userContactNumbers:
        if recipient:
            client.messages.create(to=recipient, from_=settings.TWILIO_NUMBER, body=message)

    return HttpResponse("messages sent", 200)
