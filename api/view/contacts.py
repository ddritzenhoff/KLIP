from django.http import HttpResponse
from rest_framework import status
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt

from api.errors import INTERNAL_ERROR_RESPONSE, error_response, ErrorEnum
from api.models import UserContact, UserInfo
from api.serializers import UserContactSerializer
from django.http import JsonResponse
import json
from django.core.exceptions import ObjectDoesNotExist


class ContactsView(APIView):
    @csrf_exempt
    def get(self, request):
        """
           Gets all of a user's contacts
           :param request: GET request
           :return: serialized user contact data, or error if no contacts were found
       """
        userId = request.GET["userId"]
        try:
            contacts = UserContact.objects.filter(userId=userId).order_by("contactName")
            serializer = list(map(UserContactSerializer, contacts))
            return JsonResponse({'contacts': [s.data for s in serializer]}, safe=False, status=status.HTTP_200_OK)
        except Exception as e:
            return INTERNAL_ERROR_RESPONSE

    @csrf_exempt
    def post(self, request):
        """
            Adds a new contact to a user's emergency contacts (or updates it if it exists - WIP!)
            :param request: POST request
            :return: data representing the newly added/updated contact
        """
        payload = json.loads(request.body)
        userId = payload["userId"]
        phoneNumber = payload["contact"]["phoneNumber"]
        try:
            user = UserInfo.objects.get(id=userId)
        except ObjectDoesNotExist as e:
            return error_response(ErrorEnum.USER_NOT_FOUND, http_status=status.HTTP_404_NOT_FOUND)
        if UserContact.objects.filter(userId=userId, phoneNumber=phoneNumber).count() > 0:
            return error_response(ErrorEnum.CONTACT_ALREADY_EXISTS, http_status=status.HTTP_409_CONFLICT)
        try:
            contact_info = UserContact.objects.create(
                userId=user,
                contactName=payload["contact"]["contactName"],
                phoneNumber=payload["contact"]["phoneNumber"]
            )
            # what should we do if this user has added a UserContact with the same userId and phonenumber?
            # UserContact.objects.filter(userId=user.userId, phoneNumber=payload["contact"]["phoneNumber"])
            serializer = UserContactSerializer(contact_info)
            return JsonResponse({'contact': serializer.data}, safe=False, status=status.HTTP_201_CREATED)
        except Exception as e:
            return INTERNAL_ERROR_RESPONSE

    @csrf_exempt
    def delete(self, request):
        contact_id = request.GET["contactId"]
        try:
            UserContact.objects.filter(id=contact_id).delete()
            return HttpResponse(status=status.HTTP_204_NO_CONTENT)
        except ObjectDoesNotExist as e:
            return JsonResponse({'error': str(e)}, safe=False, status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return JsonResponse({'error': 'Something terrible went wrong'}, safe=False,
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @csrf_exempt
    def put(self, request):
        """
            Updates a UserContact by user ID and contact's name
            :param request: PUT request data
            :returns: serialized data if the update succeeded, error message otherwise
            """
        payload = json.loads(request.body)
        contact_dict = payload["contact"]
        try:
            UserContact.objects.filter(id=contact_dict["id"]).update(**payload["contact"])
            serializer = UserContactSerializer(UserContact.objects.get(id=contact_dict["id"]))
            return JsonResponse({'contact': serializer.data}, safe=False, status=status.HTTP_200_OK)

        except ObjectDoesNotExist as e:
            return JsonResponse({'error': str(e)}, safe=False, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            print(e)
            return JsonResponse({'error': 'Something went wrong!'}, safe=False,
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)