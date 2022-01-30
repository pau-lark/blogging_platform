from .forms import RegisterForm, ProfileEditForm
from .services.decorators import ajax_required
from .services.subscription_service import subscribe_user, get_user_subscriptions
from .services.users_range_service import \
    get_filtered_user_list,\
    get_sorted_user_list,\
    get_user_object
from .services.rating_service import UsersRating
from .services.decorators import query_debugger
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.views.generic.base import View, TemplateResponseMixin


RATING = UsersRating()


class RegisterView(TemplateResponseMixin, View):
    template_name = 'registration/register_form.html'

    @staticmethod
    def get_form(data=None):
        return RegisterForm(data)

    def get(self, request):
        context = {
            'form': self.get_form()
        }
        return self.render_to_response(context)

    def post(self, request):
        form = self.get_form(data=request.POST)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.set_password(form.cleaned_data['password'])
            new_user.save()
            RATING.incr_or_decr_rating_by_id(action='registration',
                                             object_id=new_user.id)
            return redirect('profile')
        context = {
            'form': form
        }
        return self.render_to_response(context)


@query_debugger
@login_required
def profile(request: HttpRequest, username: str = None) -> HttpResponse:
    if username:
        user = get_user_object(username)
    else:
        user = request.user
    user.rating = int(RATING.get_rating_by_id(user.id))
    # request.user.subscription_list = get_user_subscriptions(request.user)
    context = {
        'user': user,
        'section': 'author'
    }
    return render(request, 'users/profile/detail.html', context)


class ProfileSettingsView(TemplateResponseMixin, View):
    template_name = 'users/profile/settings.html'

    def get(self, request):
        form = ProfileEditForm(instance=request.user)
        return self.render_to_response({'form': form})

    def post(self, request):
        form = ProfileEditForm(instance=request.user,
                               data=request.POST,
                               files=request.FILES)
        if form.is_valid():
            form.save()
            return redirect('profile')
        return self.render_to_response({'form': form})


@query_debugger
@login_required
def user_list_view(request: HttpRequest, **kwargs) -> HttpResponse:
    filter_by = kwargs.get('filter_by')
    order_by = kwargs.get('order_by')
    username = kwargs.get('username')
    if not username:
        username = request.user.username

    users = get_filtered_user_list(username, filter_by)
    users = get_sorted_user_list(users, order_by)

    for user in users:
        user.rating = RATING.get_rating_by_id(user.id)

    request.user.subscription_list = get_user_subscriptions(request.user)
    context = {
        'users': users,
        'section': 'author',
        'username': username,
        'filter': filter_by,
        'order': order_by
    }
    return render(request, 'users/list.html', context)


@login_required
@require_POST
def follow_user(request):
    username = request.POST.get('username')
    action = request.POST.get('action')
    if username and action:
        if subscribe_user(from_user=request.user,
                          to_user_username=username,
                          action=action):
            return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': ''})
