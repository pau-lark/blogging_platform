from .forms import RegisterForm
from .models import CustomUser
from .services.users_range_service import \
    get_filtered_user_list,\
    get_sorted_user_list,\
    get_user_object
from blog.common.decorators import query_debugger
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views.generic.base import View, TemplateResponseMixin


class RegisterView(TemplateResponseMixin, View):
    template_name = 'registration/register_form.html'

    @staticmethod
    def get_form(data=None):
        return RegisterForm(data)

    def get(self, request, *args, **kwargs):
        context = {
            'form': self.get_form()
        }
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        form = self.get_form(data=request.POST)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.set_password(form.cleaned_data['password'])
            new_user.save()
            return render(request, 'registration/register_done.html')
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
    context = {
        'user': user,
        'section': 'author'
    }
    return render(request, 'users/profile/detail.html', context)



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
    context = {
        'users': users,
        'section': 'author',
        'username': username,
        'filter': filter_by,
        'order': order_by
    }
    return render(request, 'users/list.html', context)


"""
class AuthorListView(TemplateResponseMixin, View):
    template_name = 'users/list.html'

    def get(self, request):
        authors = CustomUser.objects.all()
        context = {
            'authors': authors,
            'section': 'author'
        }
        return self.render_to_response(context)



class AuthorDetailView(TemplateResponseMixin, View):
    template_name = 'users/profile/detail.html'

    def get(self, request, username):
        author = get_object_or_404(CustomUser,
                                   username=username)
        context = {
            'author': author,
            'section': 'author'
        }
        return self.render_to_response(context)
"""