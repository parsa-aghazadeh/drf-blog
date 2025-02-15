from rest_framework import serializers
from apps.blog_backend.models import User,Post,Comment,SiteInfo

class LoginSerializer(serializers.Serializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'password')


class LogoutSerializer(serializers.Serializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'password')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('title' , 'content')

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("content",)


class SiteInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteInfo
        fields = '__all__'