from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from core.settings import AUTH_USER_MODEL

class User(AbstractUser):
    forget_token = models.CharField(max_length=50,blank=True,null=True)
    class Roles(models.TextChoices):
        ADMIN = 1
        USER = 2
    role = models.IntegerField(choices=Roles.choices, default=Roles.USER)


class Post(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    content = models.TextField(blank=True, max_length=50000)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(null=True)
    deleted_at = models.DateTimeField(null=True)
    likes = models.ManyToManyField(User, related_name="user_post")
    saved = models.ManyToManyField(User, related_name="user_save_post")
    verified = models.BooleanField(default=False)


class Comment(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=False)


class SiteInfo(models.Model):
    title = models.CharField(max_length=50)
    support_email = models.EmailField()
    support_phone_number = models.CharField(max_length=11)
    application = models.CharField(max_length=30)
    status = models.CharField(max_length=10)
    version = models.CharField(max_length=30)
