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
from .services.view_mixins import PaginatorMixin, PostEditMixin
from .services.post_rating_service import PostsRating, PostViewCounter
from account.services.decorators import query_debugger
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.generic.base import View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.shortcuts import render
from django.urls import reverse_lazy

from django.contrib.contenttypes.models import ContentType
from django.forms.models import modelform_factory


RATING = PostsRating()


def index(request):
    form = SearchForm()
    return render(request, 'base.html', {'search_form': form})


class PostListBaseView(PaginatorMixin, View):
    """
    Базовый view для вывода фильтрованного списка статей для
    авторизованного пользователя
    и списка всех статей для неавторизованного.
    Также производится сортировка и фильтрация по категориям.
    К каждой статье добавляется превью, рейтинг,
    количество лайков и просмотров.
    Для пагинации используется миксин
    """
    paginate_by = 5
    template_name = 'posts/list.html'
    post_view_counter = PostViewCounter()
    posts = None
    category = None
    username = None
    filter_by = None
    order_by = None

    @query_debugger
    def get(self, request: HttpRequest, username: str = None,
            category_slug: str = None) -> HttpResponse:

        if not self.filter_by:
            self.filter_by = request.GET.get('filter')
        self.order_by = request.GET.get('order')
        if not username and request.user.is_authenticated:
            self.username = request.user.username
        if category_slug:
            self.category = get_category_by_slug(category_slug)

        posts = get_filtered_and_sorted_post_list(self.username,
                                                  category_slug,
                                                  self.filter_by,
                                                  self.order_by)
        for post in posts:
            post = self.get_post_content_and_attrs(post)
        self.posts = posts

        return render(request, self.template_name, self.get_context_data())

    def get_post_content_and_attrs(self, post: Post):
        post.preview_content = get_text_preview_for_post(post)
        post.rating = RATING.get_rating_by_id(post.id)
        post.view_count = self.post_view_counter.get_post_view_count(post.id)
        # TODO: comments
        post.comments_count = 0
        return post

    def get_context_data(self):
        context = {
            'posts': self.get_paginate_list(self.posts),
            'category': self.category,
            'username': self.username,
            'filter': self.filter_by,
            'order': self.order_by,
            'section': 'post'
        }
        return context


class PostListView(PostListBaseView):
    """
    View для отображения главной страницы с постами
    Если пользователь не авторизован, ему недоступны фильтры
    """
    def get_context_data(self):
        context = super().get_context_data()
        context['order_list'] = settings.POST_ORDER_LIST
        if self.request.user.is_authenticated:
            context['filter_list'] = settings.POST_FILTER_LIST
        return context


class UserPostListView(PostListBaseView):
    """
    View для вывода списка статей выбранного пользователя.
    Для собственный постов возможна фильтрация по статусу,
    чужие посты выводятся со статусом 'опубликовано'
    """
    def get(self, request: HttpRequest,
            username: str = None,
            category_slug: str = None) -> HttpResponse:

        if self.username != self.request.user.username:
            self.filter_by = 'publish'
        return super().get(request, username, category_slug)

    def get_context_data(self):
        context = super().get_context_data()
        if self.username == self.request.user.username:
            context['filter_list'] = settings.USER_POST_STATUS_FILTER_LIST
        if self.filter_by == 'publish':
            context['order_list'] = settings.POST_ORDER_LIST
        else:
            self.template_name = 'posts/draft_list.html'


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
