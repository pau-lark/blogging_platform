from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('posts/create/',
         views.PostCreateView.as_view(),
         name='post_create'),
    path('posts/edit/header/<int:post_id>/',
         views.PostUpdateView.as_view(),
         name='post_header_edit'),
    path('posts/delete/<int:post_id>/',
         views.PostDeleteView.as_view(),
         name='post_delete'),
    path('posts/edit/<int:post_id>/',
         views.PostPreviewEditView.as_view(),
         name='post_edit'),
    path('posts/',
         views.PostListView.as_view(),
         name='post_list'),
    path('posts/<slug:category_slug>/',
         views.PostListView.as_view(),
         name='post_list_by_category'),
    path('<str:username>/posts/',
         views.UserPostListView.as_view(),
         name='users_post_list'),
    path('<str:username>/posts/<slug:category_slug>/',
         views.UserPostListView.as_view(),
         name='users_post_list_by_category'),
    path('posts/detail/<int:post_id>/',
         views.PostDetailView.as_view(),
         name='post_detail'),
]
