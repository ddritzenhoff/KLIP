from rest_framework import status
from django.http import JsonResponse
from enum import Enum

class ErrorEnum(Enum):
    UNRECOGNIZED_LOGIN_INFO = "Unrecognized_Login_Info"
    EMAIL_ALREADY_REGISTERED = "Email_Already_Registered"
    USER_NOT_FOUND = "User_Not_Found"
    CONTACT_NOT_FOUND = "Contact_Not_Found"
    CONTACT_ALREADY_EXISTS = "Contact_Already_Exists"
    POSTS_NOT_FOUND = "Posts_Not_Found"
    UNKNOWN_ERROR = "Unknown_Error"
    NO_USER_CONTACTS = "No_User_Contacts"

def error_response(error_cause: ErrorEnum,
                    http_status=status.HTTP_500_INTERNAL_SERVER_ERROR) -> JsonResponse:
    """
    Generates an HttpResponse when an exception occurs
    :param e: the exception
    :param message: the message that should be included with the response (defaults to the error message)
    :param http_status: the HTTP status that should be included with the HttpResponse
    :return: the HttpResponse
    """
    return JsonResponse({"error": str(error_cause.value)},
                         safe=False,
                         status=http_status)

INTERNAL_ERROR_RESPONSE = error_response(ErrorEnum.UNKNOWN_ERROR, http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


