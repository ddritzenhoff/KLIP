from django.http import HttpResponse
from rest_framework import status
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt

from api.errors import error_response, INTERNAL_ERROR_RESPONSE, ErrorEnum
from api.models import CommunityPost, UserInfo
from api.serializers import PostSerializer
from django.http import JsonResponse
import json
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.pagination import PageNumberPagination


class PostsView(APIView):
    @csrf_exempt
    def get(self, request):
        """
            Gets recent community posts by timestamp
            :param request: GET request
            :return: ALL community posts with the newest posts first, or an error if something went wrong
        """
        try:
            posts = CommunityPost.objects.all().order_by('timestamp')
            serializers = list(map(PostSerializer, posts))
            return JsonResponse({'posts': [s.data for s in serializers]}, safe=False, status=status.HTTP_200_OK)
        except ObjectDoesNotExist as e:
            return JsonResponse(ErrorEnum.POSTS_NOT_FOUND, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return INTERNAL_ERROR_RESPONSE

    @csrf_exempt
    def post(self, request):
        """
           Creates a new community post
           :param request: POST request
           :return: data representing the community post that the user just made
        """
        payload = json.loads(json.dumps(request.data))
        try:
            user = UserInfo.objects.get(id=payload["userId"])
            community_post = CommunityPost.objects.create(
                text=payload["text"],
                longitude=payload["longitude"],
                latitude=payload["latitude"],
                userId=user
            )
            serializer = PostSerializer(community_post)
            return JsonResponse({'post': serializer.data}, safe=False, status=status.HTTP_201_CREATED)
        except ObjectDoesNotExist as e:
            return error_response(ErrorEnum.USER_NOT_FOUND, http_status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return INTERNAL_ERROR_RESPONSE

    @csrf_exempt
    def delete(self, request):
        postId = request.GET["id"]
        try:
            # TODO returns 204 if the postId does not exist
            CommunityPost.objects.filter(id=postId).delete()
            return HttpResponse(status=status.HTTP_204_NO_CONTENT)
        except ObjectDoesNotExist:
            return error_response(ErrorEnum.POSTS_NOT_FOUND, http_status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return INTERNAL_ERROR_RESPONSE


class PostsList(APIView, PageNumberPagination):
    # number of items per page by default
    page_size = 20
    # max number of items per page
    max_page_size = 20

    def get_queryset(self):
        posts = CommunityPost.objects.all().order_by('timestamp')
        return self.paginate_queryset(posts, self.request)

    def get(self, request):
        posts = self.get_queryset()
        serializer = PostSerializer(posts, many=True)
        return self.get_paginated_response(serializer.data)
