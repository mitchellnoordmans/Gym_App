from django.contrib import admin

# Register your models here.

from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model




# admin.site.unregister(User)
# Register your models here.

from .models import  ContactForm, Comment, UserProfile, ProfilePost, News

admin.site.register(News)
admin.site.register(ContactForm)
admin.site.register(Comment)
admin.site.register(UserProfile)
admin.site.register(ProfilePost)