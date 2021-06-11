from django.urls import path
from . import views
from .view.contacts import ContactsView
from .view.posts import PostsView, PostsList
from .view import emergency

urlpatterns = [
  path('v1/login', views.login),
  path('v1/signup', views.signup),
  path('v1/posts', PostsView.as_view()),
  path('v1/contacts', ContactsView.as_view()),
  path('v1/posts/paginated', PostsList.as_view()),
  path('v1/emergency', emergency.handle_emergency_request),
]