# from contextlib import nullcontext
# from itertools import count
# from lib2to3.fixes.fix_input import context
# from math import trunc
# from pyexpat.errors import messages
# from xml.sax.expatreader import version
#
# from django.core.serializers import serialize
# from django.shortcuts import render
from http.client import responses

from django.core.serializers import serialize
from django.template.defaultfilters import title

from apps.blog_backend.models import Post, Comment, User , SiteInfo
from apps.blog_backend.serializers import UserSerializer, PostSerializer, CommentSerializer, LoginSerializer, SiteInfoSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import FileResponse, HttpResponse
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from datetime import date, datetime
from django.db.models import Q, Count, Sum, F
from .pagination import CustomPagination
from django.core.files.storage import default_storage
import uuid
import os
from django.conf import settings
from core import settings




class Register(APIView):
    def post(self,request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            if request.data['password'] == request.data['password_confirm']:
                try:
                    User.objects.create_user(serializer.data['username'],serializer.data['email'],serializer.data['password'])
                    return Response({'messages' : 'Successfully registered'} , status=status.HTTP_201_CREATED)
                except IntegrityError as e:
                    if e.args[0] == 1062:
                        return Response({'messages' : 'User already exists'} , status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'messages' : 'Passwords do not match'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Login(APIView):
    def post(self,request):
        data = request.POST
        serializer = LoginSerializer(data=data)
        if serializer.is_valid():
            user = authenticate(username=data["username"], password=data["password"])
            # user = User.objects.filter(username=serializer.data['username'], password=serializer.data['password'])
            if user is not None:
                token,create = Token.objects.get_or_create(user =user)
                if not create:
                    token.delete()
                    token = Token.objects.create(user=user)
                return Response({'token': token.key, "Success": "Login SuccessFully"}, status=status.HTTP_201_CREATED)
            else:
                return Response({'message':'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Logout(APIView):
    def post(self,request):
        if request.user.is_authenticated:
            try:
                token = Token.objects.get(user=request.user)
                token.delete()
                return Response({"success": "logout SuccessFully"}, status=status.HTTP_200_OK)
            except Token.DoesNotExist:
                return Response({"message":"this user not logged in"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "user is unauthenticated"},status=status.HTTP_401_UNAUTHORIZED)

class Profile(APIView):
    def get(self,request):
        if request.user.is_authenticated:
            context = {
                "username": request.user.username,
                "email": request.user.email,
                "first_name": request.user.first_name,
                "last_name": request.user.last_name
            }
            return Response(context)
        return Response({"message": "user is unauthenticated"},status=status.HTTP_401_UNAUTHORIZED)



class PostCreate(APIView):
    def post(self, request):
        if not request.user.is_authenticated:
            return Response({"message": "user is unauthenticated"},status=status.HTTP_401_UNAUTHORIZED)
        data = request.POST
        serializer = PostSerializer(data=data)
        if serializer.is_valid():
            data = serializer.data
            data['user'] = request.user
            data['created_at'] = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            if request.user.role == int(User.Roles.ADMIN):
                data['verified'] = True
            Post.objects.create(**data)
            return Response({"message": "The post created successfully"}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AddComment(APIView):
    def post(self, request, post_id):
        if not request.user.is_authenticated:
            return Response({"message": "user is unauthenticated"},status=status.HTTP_401_UNAUTHORIZED)
        post = Post.objects.get(pk=post_id)
        data = request.data
        serializer = CommentSerializer(data=data)
        if serializer.is_valid():
            data = serializer.data
            if request.user.role == int(User.Roles.ADMIN):
                data['verified'] = True
            Comment.objects.create(user=request.user,post=post,content=data['content'],verified=data['verified'])
            return Response({"success":"comment added successfully"}, status=status.HTTP_201_CREATED)
        else:
            return Response({"errors":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class Search(APIView):
    def get(self, request):
        if "q" in request.GET:
            posts = Post.objects.filter(Q(content__contains=request.GET['q']) | Q(title__contains=request.GET['q'])).values('title', 'id')
            if not posts:
                return Response({"message": "sorry no result"}, status=204)
            context = {"posts": list(posts)}
            return Response(context)
        else:
            return Response({"message": "sorry no result"}, status=204)

class Like(APIView):
    def get(self, request, post_id):
        try:
            post = Post.objects.get(pk=post_id)
            total_likes = post.likes.count()
            context = {"total_likes": total_likes}
            return Response(context)
        except Post.DoesNotExist:
            error = {"error": "Post not found"}
            return Response(error, status=404)

    def post(self, request, post_id):
        if request.user.is_authenticated:
            try:
                user = request.user
                post = Post.objects.get(pk=post_id)
                if user in post.likes.all():
                    post.likes.remove(user)
                    total_likes = post.likes.count()
                    context = {"total_likes": total_likes,
                               "like_status": 'disliked'}
                    return Response(context)
                else:
                    post.likes.add(user)
                    total_likes = post.likes.count()
                    context = {"total_likes": total_likes,
                               "like_status": 'liked'}
                    return Response(context)
            except Post.DoesNotExist:
                error = {"error": "Post not found"}
                return Response(error, status=404)
        else:
            return Response({"message": "user is unauthenticated"}, status=401)

class Save(APIView):
    def get(self, request, post_id):
        post = Post.objects.get(pk=post_id)
        total_save = post.saved.count()
        return Response({"total_save": total_save})

    def post(self, request, post_id):
        try:
            if request.user.is_authenticated:
                user = request.user
                post = Post.objects.get(pk=post_id)
                if user in post.saved.all():
                    post.saved.remove(user)
                    total_save = post.saved.count()
                    return Response({"save_status": " unsaved", "total_save": total_save})
                else:
                    post.saved.add(user)
                    total_save = post.saved.count()
                    return Response({"save_status": "saved", "total_save": total_save})
            else:
                return Response({"message": "user is unauthenticated"}, status=401)
        except Post.DoesNotExist:
            return Response({"message": "post not found"}, status=404)


class GetAllPosts(APIView):
    def get(self, request):
        if request.user.is_authenticated:
            posts = Post.objects.filter(verified=1).annotate(
                short_content=F('content')[:100]
            ).values('title', 'id', 'short_content')
            context = {"posts": list(posts)}
            return Response(context)
        else:
            return Response({"message": "user is unauthenticated"}, status=401)

class PostListView(APIView):
    pagination_class = CustomPagination

    def get(self, request):
        queryset = Post.objects.all()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)

        if page is not None:
            serializer = PostSerializer(page, many=True)
            return paginator.get_paginated_response(data=serializer.data)
        return Response(status=status.HTTP_404_NOT_FOUND)


class CommentListView(APIView):
    pagination_class = CustomPagination
    def get(self, request, post_id):
        queryset = Comment.objects.filter(post_id=post_id)
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)
        if page is not None:
            serializer = CommentSerializer(page, many=True)
            return paginator.get_paginated_response(data=serializer.data)
        return Response(status=status.HTTP_404_NOT_FOUND)

class AdminPosts(APIView):
    def get(self, request):
        if request.user.is_authenticated and request.user.role == int(User.Roles.ADMIN):
            if request.query_params:
                if request.query_params.get('verified') == '1':
                    posts = Post.objects.filter(verified=1)
                    serializer = PostSerializer(posts, many=True)
                    return Response(serializer.data)
                elif request.query_params.get('verified') == '0':
                    posts = Post.objects.filter(verified=0)
                    serializer = PostSerializer(posts, many=True)
                    return Response(serializer.data)

            posts = Post.objects.all()
            serializer = PostSerializer(posts, many=True)
            return Response(serializer.data)
        else:
            return Response({"message": "user is unauthenticated"}, status=401)

class AdminComments(APIView):
    def get(self,request):
        if request.user.is_authenticated and request.user.role == int(User.Roles.ADMIN):
            if request.query_params:
                if request.query_params.get('verified') == '1':
                    comments = Comment.objects.filter(verified=1)
                    serializer = CommentSerializer(comments, many=True)
                    return Response(serializer.data)
                elif request.query_params.get('verified') == '0':
                    comments = Comment.objects.filter(verified=0)
                    serializer = CommentSerializer(comments, many=True)
                    return Response(serializer.data)

            comments = Comment.objects.all()
            serializer = CommentSerializer(comments, many=True)
            return Response(serializer.data)
        else:
            return Response({"message": "user is unauthenticated"}, status=401)



class PostVerify(APIView):
    def post(self, request, post_id):
        try:
            if Post.objects.get(pk=post_id):
                if request.user.is_authenticated and request.user.role == int(User.Roles.ADMIN):
                    Post.objects.filter(pk=post_id).update(verified=1)
                    return Response({"message": "Post verified"}, status=201)
                else:
                    return Response({"message": "user is unauthenticated"}, status=401)
        except Post.DoesNotExist:
            return Response({"message": "post not found"}, status=404)

class CommentVerify(APIView):
    def post(self, request, comment_id):
        try:
            if Comment.objects.get(pk=comment_id):
                if request.user.is_authenticated and request.user.role == int(User.Roles.ADMIN):
                    Comment.objects.filter(pk=comment_id).update(verified=1)
                    return Response({"message": "comment verified"}, status=201)
                else:
                    return Response({"message": "user is unauthenticated"}, status=401)
        except Comment.DoesNotExist:
            return Response({"message": "comment not found"}, status=404)

class AdminPostDelete(APIView):
    def delete(self, request, post_id):
        if request.user.is_authenticated and request.user.role == int(User.Roles.ADMIN):
            try:
                post = Post.objects.get(pk=post_id)
                post.delete()
                return Response({'message':'post deleted successfully'},status=200)
            except Post.DoesNotExist:
                return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"message": "user is unauthenticated"}, status=401)

class AdminCommentDelete(APIView):
    def delete(self, request, comment_id):
        if request.user.is_authenticated and request.user.role == int(User.Roles.ADMIN):
            try:
                comment = Comment.objects.get(pk=comment_id)
                comment.delete()
                return Response({'message':'comment deleted successfully'},status=200)
            except Comment.DoesNotExist:
                return Response({'error': 'comment not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"message": "user is unauthenticated"}, status=401)


class AdminUserDelete(APIView):
    def delete(self,request,user_id):
        if request.user.is_authenticated and request.user.role == int(User.Roles.ADMIN):
            try:
                user = User.objects.get(pk=user_id)
                if user.role == int(User.Roles.ADMIN):
                    return Response({'message':'You cannot delete the admin'})
                user.delete()
                return Response({'message':'user deleted successfully'},status=200)
            except User.DoesNotExist:
                return Response({'error': 'user not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"message": "user is unauthenticated"}, status=401)

class PostDeleteByCreator(APIView):
    def delete(self,request,post_id):
        if request.user.is_authenticated:
            try:
                post = Post.objects.get(pk=post_id)
                if post.user == request.user:
                    post.delete()
                    return Response({'message':'post deleted successfully'},status=200)
            except Post.DoesNotExist:
                return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'error': 'user is unauthenticated'}, status=401)


class CommentDeleteByCreator(APIView):
    def delete(self,request,comment_id):
        if request.user.is_authenticated:
            try:
                comment = Comment.objects.get(pk=comment_id)
                if comment.user == request.user:
                    comment.delete()
                    return Response({'message':'comment deleted successfully'},status=200)
            except Comment.DoesNotExist:
                return Response({'error': 'comment not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'error': 'user is unauthenticated'}, status=401)



class PostUpdate(APIView):
    def patch(self, request, post_id):
        if request.user.is_authenticated:
            try:
                post = Post.objects.get(pk=post_id)
                if post.user == request.user:
                    serializer = PostSerializer(post, data=request.data , partial=True)
                    if serializer.is_valid():
                        serializer.save()
                        return Response({'message':f'updated post by {serializer.data} successfully'}, status=200)
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except Post.DoesNotExist:
                return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'error': 'user is unauthenticated'}, status=401)



class CommentUpdate(APIView):
    def patch(self, request, comment_id):
        if request.user.is_authenticated:
            try:
                comment = Comment.objects.get(pk=comment_id)
                if comment.user == request.user:
                    serializer = CommentSerializer(comment, data=request.data , partial=True)
                    if serializer.is_valid():
                        serializer.save()
                        return Response({'message':f'updated comment by {serializer.data} successfully'}, status=200)
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except Comment.DoesNotExist:
                return Response({'error': 'comment not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'error': 'user is unauthenticated'}, status=401)


class GetGeneralSiteInformation(APIView):
    def get(self,request):
        data = SiteInfo.objects.get(id=1)
        context = {
            'application'   : data.application,
            'status'        : data.status,
            'version'       : data.version,
            'title'         : data.title,
            'support_email' : data.support_email,
            'support_mobile': data.support_phone_number,
        }
        return Response(context)



class AdminSiteInfoUpdate(APIView):
    def patch(self, request):
        if request.user.is_authenticated and request.user.role == int(User.Roles.ADMIN):
            obj = SiteInfo.objects.get(pk=1)
            serializer = SiteInfoSerializer(obj, data=request.data , partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'message':'updated site information successfully'}, status=200)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': 'user is unauthenticated'}, status=401)



 
class UsersList(APIView):
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)



class UploadImage(APIView):
    def post(self, request):
        file = self.request.FILES['image']
        file_id = uuid.uuid4()
        file_name = f'{file_id}.{file.name.split(".")[-1]}'
        print()
        file_path = default_storage.save(file_name, file)
        file_url = os.path.join(settings.MEDIA_URL, file_path)
        return Response({'file_url': file_url,'file_id':file_id})


class DownloadImage(APIView):
    def get(self, request, file_id):
        try:
            file_name = f"{file_id}.jpg"
            file_path = os.path.join(settings.MEDIA_ROOT, f'{file_id}.{file_name.split(".")[-1]}')

            if os.path.exists(file_path):
                with open(file_path, 'rb') as file:
                    response = HttpResponse(file.read(), content_type='image/jpg')
                    response['Content-Disposition'] = 'attachment; filename='+(os.path.basename(file_path))+'.jpg'
                    return response
            else:
                return Response({'error': 'File not found'}, status=404)
        except FileNotFoundError:
            return Response({'error': 'File not found'}, status=404)