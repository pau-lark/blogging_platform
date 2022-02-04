from .forms import SearchForm, PostCreationForm
from .models import Post, Category
from .services.post_content_service import \
    get_text_preview_for_post,\
    get_post_content
from .services.posts_range_service import \
    get_filtered_and_sorted_post_list,\
    get_category_by_slug,\
    get_post_object,\
    get_draft_list
from .services.view_mixins import PaginatorMixin
from .services.post_rating_service import PostsRating, PostViewCounter
from account.services.decorators import query_debugger
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.generic.base import View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy

from django.contrib.contenttypes.models import ContentType
from django.forms.models import modelform_factory


RATING = PostsRating()


def index(request):
    form = SearchForm()
    return render(request, 'base.html', {'search_form': form})





# TODO: пагинация
class PostListView(PaginatorMixin, View):
    """
    View для вывода фильтрованного списка статей для
    авторизованного пользователя
    и списка всех статей для неавторизованного.
    Также производится сортировка и фильтрация по категориям.
    К каждой статье добавляется превью, рейтинг,
    количество лайков и просмотров
    """
    paginate_by = 5
    category = None
    template_name = 'posts/list.html'
    post_view_counter = PostViewCounter()

    @query_debugger
    def get(self, request: HttpRequest,
            username: str = None,
            category_slug: str = None) -> HttpResponse:
        filter_by = request.GET.get('filter')
        order_by = request.GET.get('order')
        if not username and request.user.is_authenticated:
            username = request.user.username

        posts = get_filtered_and_sorted_post_list(username,
                                                  category_slug,
                                                  filter_by,
                                                  order_by)

        for post in posts:
            post.preview_content = get_text_preview_for_post(post)
            post.rating = RATING.get_rating_by_id(post.id)
            post.view_count = self.post_view_counter.get_post_view_count(post.id)
            # TODO: comments
            post.comments_count = 0

        if category_slug:
            self.category = get_category_by_slug(category_slug)

        context = {
            'posts': self.get_paginate_list(posts),
            'category': self.category,
            'username': username,
            'section': 'post',
            'filter': filter_by,
            'order': order_by
        }

        return render(request, self.template_name, context)


class DraftListView(LoginRequiredMixin, PaginatorMixin, View):
    """View для вывода списка черновиков"""
    paginate_by = 5
    template_name = 'posts/draft_list.html'

    def get(self, request):
        drafts = get_draft_list(request.user)
        context = {
            'posts': self.get_paginate_list(drafts),
            'sidebar_status': 'draft'
        }
        return render(request, self.template_name, context)


class PostDetailView(View):
    post_view_counter = PostViewCounter()

    @query_debugger
    def get(self, request: HttpRequest, post_id: int) -> HttpResponse:
        post = get_post_object(post_id)
        contents = get_post_content(post)
        post.rating = RATING.get_rating_by_id(post.id)
        post.view_count = self.post_view_counter.get_post_view_count(post_id)
        # TODO: likes, comments, forms

        self.post_view_counter.incr_view_count(post_id)

        context = {
            'post': post,
            'contents': contents,
            'section': post
        }
        return render(request, 'posts/detail.html', context)


class PostEditMixin:
    form_class = PostCreationForm
    model = Post
    success_url = None
    template_name = 'posts/edit/create_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        self.success_url = reverse_lazy('blog:post_edit',
                                        kwargs={'post_id': self.object.id})
        return super().get_success_url()


class PostCreateView(LoginRequiredMixin, PostEditMixin, CreateView):
    pass


class PostUpdateView(LoginRequiredMixin, PostEditMixin, UpdateView):
    pk_url_kwarg = 'post_id'


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    pk_url_kwarg = 'post_id'
    success_url = reverse_lazy('blog:draft_list')
    template_name = 'posts/edit/delete_form.html'

    def delete(self, request, *args, **kwargs):
        post = self.get_object()
        for content in post.contents.all():
            content.content_object.delete()
        return super().delete(request, *args, **kwargs)


class PostPreviewEditView(LoginRequiredMixin, View):
    @query_debugger
    def get(self, request: HttpRequest, post_id: int) -> HttpResponse:
        post = get_post_object(post_id)
        contents = get_post_content(post)

        context = {
            'post': post,
            'contents': contents
        }
        return render(request, 'posts/edit/preview.html', context)
