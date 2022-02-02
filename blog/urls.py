from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('posts/create/',
         views.PostCreateUpdateView.as_view(),
         name='post_create'),
    path('posts/create/add_content/',
         views.PostContentAjaxCreateView.as_view(),
         name='add_post_content'),
    path('posts/',
         views.PostListView.as_view(),
         name='post_list'),
    path('posts/<slug:category_slug>/',
         views.PostListView.as_view(),
         name='post_list_by_category'),
    path('<str:username>/posts/',
         views.PostListView.as_view(),
         name='users_post_list'),
    path('<str:username>/posts/<slug:category_slug>/',
         views.PostListView.as_view(),
         name='users_post_list_by_category'),
    path('posts/detail/<int:post_id>/',
         views.PostDetailView.as_view(),
         name='post_detail'),
]
