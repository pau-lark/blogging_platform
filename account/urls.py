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
    path('profile/', views.profile,
         name='profile'),
    path('profile/<str:username>/', views.profile,
         name='user_profile'),
    path('author_list/<str:filter_by>/<str:order_by>/',
         views.user_list_view,
         name='my_user_list'),
    path('author_list/<str:username>/<str:filter_by>/<str:order_by>/',
         views.user_list_view,
         name='user_list'),
]
