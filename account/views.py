from django.shortcuts import render, get_object_or_404
from .forms import RegisterForm
from django.views.generic.base import View, TemplateResponseMixin
from .models import CustomUser
from .services.users_range import get_filtered_user_list, get_sorted_user_list
from django.contrib.auth.decorators import login_required


# Мысль, убрать на хуй TRM
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


@login_required
def author_list_view(request, filter_by=None):
    authors = get_filtered_user_list(username=request.user.username,
                                     filter_by=filter_by)
    authors = get_sorted_user_list(user_list=authors)
    context = {
        'authors': authors,
        'section': 'author',
        'filter': filter_by
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
"""


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
