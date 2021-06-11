from rest_framework import serializers
from .models import user_info
from .models import CommunityPost
from .models import UserContact


class user_info_Serializer(serializers.ModelSerializer):
    class Meta:
        model = user_info
        fields = ['id',
                  'name',
                  'email',
                  'password']


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunityPost
        fields = ['id',
                  'text',
                  'longitude',
                  'latitude',
                  'userId',
                  'timestamp']


class UserContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserContact
        fields = ['id',
                  'userId',
                  'phoneNumber',
                  'contactName']
