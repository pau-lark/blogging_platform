from .forms import RegisterForm, ProfileEditForm
from .services.subscription_service import \
    subscribe_user, \
    get_user_subscriptions
from .services.users_range_service import \
    get_filtered_and_sorted_user_list,\
    get_user_object
from .services.rating_service import UsersRating
from blog.services.view_mixins import PaginatorMixin
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views.generic.base import View


class RegisterView(View):
    """
    View для регистрации пользователей
    После регистрации пользователь добавляется в redis c рейтингом 0
    """
    rating = UsersRating()
    template_name = 'registration/register_form.html'

    def get(self, request):
        form = RegisterForm()
        render(request, self.template_name, {'form': form})

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.set_password(form.cleaned_data['password'])
            new_user.save()
            self.rating.incr_or_decr_rating_by_id(action='init',
                                                  object_id=new_user.id)
            return redirect('profile')
        return render(request, self.template_name, {'form': form})


class ProfileView(LoginRequiredMixin, View):
    template_name = 'users/profile/detail.html'

    def get(self, request: HttpRequest, username: str = None) -> HttpResponse:
        if username:
            user = get_user_object(username)
        else:
            user = request.user
        request.user.subscription_list = get_user_subscriptions(request.user)
        context = {
            'user': user,
            'section': 'author'
        }
        return render(request, self.template_name, context)


class ProfileSettingsView(LoginRequiredMixin, View):
    """Редактирование информации о пользователе"""
    template_name = 'users/profile/settings.html'

    def get(self, request):
        form = ProfileEditForm(instance=request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = ProfileEditForm(instance=request.user,
                               data=request.POST,
                               files=request.FILES)
        if form.is_valid():
            form.save()
            return redirect('profile')
        return render(request, self.template_name, {'form': form})


class UserListView(LoginRequiredMixin, PaginatorMixin, View):
    """
        View для вывода фильтрованного и сортированного списка пользователей.
        Доступен только для авторизованных пользователей.
        Для пагинации используется миксин
    """
    paginate_by = 5
    template_name = 'users/list.html'

    def get(self, request, **kwargs):
        filter_by = kwargs.get('filter_by')
        order_by = kwargs.get('order_by')
        username = kwargs.get('username')
        if not username:
            username = request.user.username

        users = get_filtered_and_sorted_user_list(username, filter_by, order_by)
        request.user.subscription_list = get_user_subscriptions(request.user)

        context = {
            'users': self.get_paginate_list(users),
            'section': 'author',
            'username': username,
            'filter': filter_by,
            'order': order_by,
            'filter_list': settings.USER_FILTER_LIST,
            'order_list': settings.USER_ORDER_LIST
        }
        return render(request, self.template_name, context)


class FollowUserView(LoginRequiredMixin, View):
    """
    Обработчик ajax-запроса, подписывающий или отписывающий пользователя,
    в зависимости от значения 'action':
        add - подписка,
        delete - отписка
    """
    def post(self, request):
        username = request.POST.get('username')
        action = request.POST.get('action')
        if username and action:
            if subscribe_user(from_user=request.user,
                              to_user_username=username,
                              action=action):
                return JsonResponse({'status': 'ok'})
        return JsonResponse({'status': ''})
