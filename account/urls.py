from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(),
         name='login'),
    path('logout/',
         auth_views.LogoutView.as_view(template_name='base.html'),
         name='logout'),
    path('password-change/', auth_views.PasswordChangeView.as_view(),
         name='password_change'),
    path('password-change-done/',
         auth_views.PasswordChangeDoneView.as_view(),
         name='password_change_done'),
    path('password-reset/', auth_views.PasswordResetView.as_view(),
         name='password_reset'),
    path('password-reset-done/',
         auth_views.PasswordResetDoneView.as_view(),
         name='password_reset_done'),
    path('<str:uidb64>/<str:token>/password-reset-confirm/',
         auth_views.PasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(),
         name='password_reset_complete'),
    path('register/', views.RegisterView.as_view(),
         name='register'),
    path('author_list/', views.author_list_view,
         name='author_list'),
    path('author_list/<str:filter_by>/', views.author_list_view,
         name='author_list_by_filter'),
    path('authors/<str:username>/', views.AuthorDetailView.as_view(),
         name='author_detail')
]
