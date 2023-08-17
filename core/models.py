from django.db import models

# Create your models here.
from datetime import timedelta
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.contrib.auth import get_user_model
from django.conf import settings
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError


class ContactForm(models.Model):
    email = models.EmailField()
    question = models.TextField()

    def __str__(self):
        return self.email


class Frequently_asked(models.Model):
    question = models.CharField(max_length=100)
    answer = models.TextField()

    def __str__(self):
        return self.question

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_of_birth = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    postal_code = models.CharField(max_length=20, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)

    # Add any other custom fields or methods you need
    bio = models.TextField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    personal_trainer = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
    

class ProfilePost(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='posts')
    caption = models.CharField(max_length=300)
    image = models.FileField(upload_to='profile_posts/', null=True, blank=True)
    video = models.FileField(upload_to='profile_posts/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def validate_at_least_one_field(self):
        if not self.image and not self.video:
            raise ValidationError("At least one of 'image' or 'video' fields must be filled.")

    def clean(self):
        self.validate_at_least_one_field()

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Post by {self.user.user.username}"

class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    profile_post = models.ForeignKey(ProfilePost, on_delete=models.CASCADE, null=True)

    def __str__(self):
        if self.profile_post is not None:
            return f"{self.user.username} - {self.profile_post.caption}"
        else:
            return f"{self.user.username} - Comment without associated post"
        
class News(models.Model):
    title = models.CharField(max_length=100)
    body = models.TextField()
    create_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title