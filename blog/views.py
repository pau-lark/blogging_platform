from .forms import SearchForm
from .models import Post, Comment
from .services.post_content_service import \
    get_text_preview_for_post,\
    get_post_render_contents,\
    get_model_by_name,\
    get_content_object_by_model_name_and_id,\
    create_content,\
    delete_post_content_by_id,\
    publish_post,\
    delete_all_post_content
from .services.post_like_service import like_post
from .services.posts_range_service import \
    get_filtered_and_sorted_post_list,\
    get_post_object
from .services.view_mixins import PaginatorMixin, PostEditMixin, PostAttrsMixin
from account.services.decorators import query_debugger
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms.models import modelform_factory
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.generic.base import View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy


def index(request):
    form = SearchForm()
    return render(request, 'base.html', {'search_form': form})


class PostListBaseView(PaginatorMixin, PostAttrsMixin, View):
    """
    Базовая view для вывода фильтрованного списка статей для
    авторизованного пользователя
    и списка всех статей для неавторизованного.
    Также производится сортировка и фильтрация по категориям.
    К каждой статье добавляется превью, рейтинг,
    количество лайков и просмотров.
    Для пагинации используется миксин
    """
    paginate_by = 5
    template_name = 'posts/list.html'
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
        else:
            self.username = username
        if category_slug:
            self.category = self.get_category_by_slug(category_slug)

        posts = get_filtered_and_sorted_post_list(self.username,
                                                  category_slug,
                                                  self.filter_by,
                                                  self.order_by)
        if posts:
            for post in posts:
                post = self.get_post_content_and_attrs(post)
            self.posts = self.get_paginate_list(posts)

        return render(request, self.template_name, self.get_context_data())

    @query_debugger
    def get_post_content_and_attrs(self, article: Post) -> Post:
        article.preview_content = get_text_preview_for_post(article)
        return super().get_post_content_and_attrs(article)

    def get_context_data(self) -> dict:
        context = {
            'posts': self.posts,
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
    def get_context_data(self) -> dict:
        context = super().get_context_data()
        context['order_list'] = settings.POST_ORDER_LIST
        if self.request.user.is_authenticated:
            context['filter_list'] = settings.POST_FILTER_LIST
        return context


class UserPostListView(LoginRequiredMixin, PostListBaseView):
    """
    View для вывода списка статей выбранного пользователя.
    Для собственный постов возможна фильтрация по статусу,
    чужие посты выводятся со статусом 'опубликовано'
    """
    template_name = 'posts/user_post_list.html'

    def get(self, request: HttpRequest,
            username: str = None,
            category_slug: str = None) -> HttpResponse:

        filter_by = request.GET.get('filter')
        if username != self.request.user.username or not filter_by:
            self.filter_by = 'publish'
        if filter_by == 'draft':
            self.template_name = 'posts/draft_list.html'
        return super().get(request, username, category_slug)

    def get_context_data(self) -> dict:
        context = super().get_context_data()
        if self.username == self.request.user.username:
            context['filter_list'] = settings.USER_POST_STATUS_FILTER_LIST
            context['mine'] = True
        if self.filter_by == 'publish':
            context['order_list'] = settings.POST_ORDER_LIST
        return context


class PostDetailView(PostAttrsMixin, View):
    template_name = 'posts/detail.html'
    article = None

    def dispatch(self, request, **kwargs):
        self.article = get_post_object(kwargs.get('post_id'))
        self.article = self.get_post_content_and_attrs(self.article)
        return super().dispatch(request, **kwargs)

    @query_debugger
    def get(self, request: HttpRequest, post_id: int) -> HttpResponse:
        self.change_post_views(post_id)
        form = self.get_comment_form()
        return render(request, self.template_name, self.get_context_data(form))

    def post(self, request: HttpRequest, post_id: int) -> HttpResponse:
        form = self.get_comment_form(data=request.POST,
                                     files=request.FILES)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = self.article
            comment.author = request.user
            comment.save()
            self.rating.incr_or_decr_rating_by_id(action='comment',
                                                  object_id=post_id)
            form = self.get_comment_form()
        return render(request, self.template_name, self.get_context_data(form))

    def get_post_content_and_attrs(self, article: Post) -> Post:
        article.content_list = get_post_render_contents(article)
        return super().get_post_content_and_attrs(article)

    @staticmethod
    def get_comment_form(**kwargs):
        form = modelform_factory(Comment, fields=['body'])
        return form(**kwargs)

    def get_context_data(self, form):
        context = {
            'post': self.article,
            'category': self.article.category,
            'form': form,
            'section': 'post'
        }
        return context


class PostCreateView(LoginRequiredMixin, PostEditMixin, CreateView):
    pass


class PostUpdateView(LoginRequiredMixin, PostEditMixin, UpdateView):
    pk_url_kwarg = 'post_id'


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    pk_url_kwarg = 'post_id'
    success_url = None
    template_name = 'posts/edit/delete_form.html'

    def delete(self, request, *args, **kwargs):
        delete_all_post_content(kwargs.get('post_id'))
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        self.success_url = reverse_lazy(
            'blog:users_post_list',
            kwargs={'username': self.request.user.username}
        )
        return super().get_success_url()


class PostPreviewEditView(LoginRequiredMixin, View):
    @query_debugger
    def get(self, request: HttpRequest, post_id: int) -> HttpResponse:
        post = get_post_object(post_id)
        contents = get_post_render_contents(post)

        context = {
            'post': post,
            'contents': contents,
            'content_types': settings.POST_CONTENT_TYPES
        }
        return render(request, 'posts/edit/preview.html', context)


class ContentCreateUpdateView(LoginRequiredMixin, View):
    model = None
    content_object = None
    template_name = 'posts/content/form.html'

    def get_form(self, **kwargs):
        form = modelform_factory(self.model, exclude=[])
        return form(**kwargs)

    def dispatch(self, request, **kwargs):
        model_name = kwargs.get('model_name')
        if model_name:
            self.model = get_model_by_name(model_name)
            content_object_id = kwargs.get('content_object_id')
            if content_object_id:
                self.content_object = get_content_object_by_model_name_and_id(model_name,
                                                                              content_object_id)
        return super().dispatch(request, **kwargs)

    def get(self, request: HttpRequest, **kwargs) -> HttpResponse:
        form = self.get_form(instance=self.content_object)
        context = {
            'form': form,
            'content': self.content_object
        }
        return render(request, self.template_name, context)

    def post(self, request: HttpRequest, **kwargs) -> HttpResponse:
        post_id = kwargs.get('post_id')
        form = self.get_form(instance=self.content_object,
                             data=request.POST,
                             files=request.FILES)
        if form.is_valid():
            content_object = form.save()
            if not self.content_object:
                create_content(post=get_post_object(post_id),
                               content_object=content_object)
            return redirect('blog:post_edit', post_id)
        context = {
            'form': form,
            'content': self.content_object
        }
        return render(request, self.template_name, context)


class ContentDeleteView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest, post_id: int, content_id: int) -> HttpResponse:
        delete_post_content_by_id(content_id)
        return redirect('blog:post_edit', post_id)


def publish_post_view(request: HttpRequest, post_id: int) -> HttpResponse:
    publish_post(post_id)
    return redirect('blog:users_post_list', request.user.username)


class PostLikeView(LoginRequiredMixin, View):
    def post(self, request):
        post_id = request.POST.get('post_id')
        action = request.POST.get('action')
        if post_id and action:
            if like_post(request.user, post_id, action):
                return JsonResponse({'status': 'ok'})
        return JsonResponse({'status': ''})
