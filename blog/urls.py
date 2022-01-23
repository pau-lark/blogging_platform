from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.index, name='index'),
    path('posts/', views.post_list_view, name='post_list'),
    path('posts/<slug:category_slug>/', views.post_list_view,
         name='post_list_by_category'),
    path('posts/<int:year>/<int:month>/<int:day>/<slug:slug>/',
         views.post_detail_view,
         name='post_detail')
]
