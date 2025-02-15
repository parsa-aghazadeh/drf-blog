"""
URL configuration for blog_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from _ast import Delete
from sys import path_hooks

from django.urls import path
from apps.blog_backend.views import Login, Register, Profile, UsersList, Logout, PostCreate, Search, Like, Save, \
    GetAllPosts, AddComment, PostVerify, AdminPosts, AdminComments, CommentVerify, AdminPostDelete, AdminCommentDelete, \
    AdminUserDelete, PostDeleteByCreator, CommentDeleteByCreator, PostUpdate, CommentUpdate, GetGeneralSiteInformation, \
    AdminSiteInfoUpdate, PostListView, CommentListView, UploadImage, DownloadImage

urlpatterns = [
    path('posts', GetAllPosts.as_view()),
    path('login', Login.as_view()),
    path('signup' , Register.as_view()),
    path('profile' , Profile.as_view()),
    path('users' , UsersList.as_view()),
    path('logout' , Logout.as_view()),
    path('post/create' , PostCreate.as_view()),
    path('search' , Search.as_view()),
    path('post/<int:post_id>/like' , Like.as_view()),
    path('post/<int:post_id>/save',Save.as_view()),
    path('post/<int:post_id>/add_comment' , AddComment.as_view()),
    # path('test', Test.as_view() ),
    path('admin/posts' , AdminPosts.as_view() ),
    path('admin/comments', AdminComments.as_view() ),
    path('post/<int:post_id>/verify' , PostVerify.as_view()),
    path('comment/<int:comment_id>/verify' , CommentVerify.as_view()),
    path('admin/user/<int:user_id>/delete', AdminUserDelete.as_view()),
    path('admin/post/<int:post_id>/delete' , AdminPostDelete.as_view()),
    path('admin/comment/<int:comment_id>/delete' , AdminCommentDelete.as_view()),
    path('post/<int:post_id>/delete', PostDeleteByCreator.as_view()),
    path('comment/<int:comment_id>/delete' , CommentDeleteByCreator.as_view()),
    path('post/<int:post_id>/update' , PostUpdate.as_view()),
    path('comment/<int:comment_id>/update' , CommentUpdate.as_view()),
    path('' , GetGeneralSiteInformation.as_view()),
    path('admin/site/info/update' , AdminSiteInfoUpdate.as_view()),
    path('pagination/posts',PostListView.as_view()),
    path('pagination/post/<int:post_id>/comments' , CommentListView.as_view()),
    path('uploade/image' , UploadImage.as_view()),
    path('download/image/<str:file_id>' , DownloadImage.as_view()),

]
