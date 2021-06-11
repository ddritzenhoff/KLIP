from django.contrib import admin
from api.models import user_info, CommunityPost, UserContact, UserInfo


admin.site.register(user_info) #TODO remove @deprecated
admin.site.register(CommunityPost)
admin.site.register(UserContact)
admin.site.register(UserInfo)