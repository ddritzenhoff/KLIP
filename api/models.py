from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import UserInfoManager


class user_info(models.Model):
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    objects = models.Manager()

    def __str__(self):
        return self.name


class UserInfo(AbstractUser):
    # Removing the username field b/c it's being replaced with email
    username = None

    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserInfoManager()

    def __str__(self):
        return self.email


class CommunityPost(models.Model):
    """Represents community posts"""
    text = models.CharField(max_length=1000)
    longitude = models.CharField(max_length=15)
    latitude = models.CharField(max_length=15)
    userId = models.ForeignKey(UserInfo, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()


class UserContact(models.Model):
    userId = models.ForeignKey(UserInfo, on_delete=models.CASCADE)
    phoneNumber = models.CharField(max_length=11)  # only numbers - no spaces, parens, or dashes
    contactName = models.CharField(max_length=50)
    objects = models.Manager()

    def __str__(self):
        return self.contactName