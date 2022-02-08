from .forms import SearchForm
from .models import Article, Comment
from .services.article_content_service import \
    get_text_preview_for_article,\
    get_article_render_contents,\
    get_model_by_name,\
    get_content_object_by_model_name_and_id,\
    create_content,\
    delete_article_content_by_id,\
    publish_article,\
    delete_all_article_content
from .services.article_like_service import like_article
from .services.article_range_service import \
    get_filtered_and_sorted_article_list,\
    get_article_object
from .services.view_mixins import PaginatorMixin, ArticleEditMixin, ArticleAttrsMixin
from account.services.decorators import query_debugger
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms.models import modelform_factory
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.generic.base import View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy


class ArticleListBaseView(PaginatorMixin, ArticleAttrsMixin, View):
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
    template_name = 'articles/list.html'
    articles = None
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

        articles = get_filtered_and_sorted_article_list(self.username,
                                                        category_slug,
                                                        self.filter_by,
                                                        self.order_by)
        if articles:
            for article in articles:
                article = self.get_article_content_and_attrs(article)
            self.articles = self.get_paginate_list(articles)

        return render(request, self.template_name, self.get_context_data())

    @query_debugger
    def get_article_content_and_attrs(self, article: Article) -> Article:
        article.preview_content = get_text_preview_for_article(article)
        return super().get_article_content_and_attrs(article)

    def get_context_data(self) -> dict:
        context = {
            'articles': self.articles,
            'category': self.category,
            'username': self.username,
            'filter': self.filter_by,
            'order': self.order_by,
            'section': 'article'
        }
        return context


class ArticleListView(ArticleListBaseView):
    """
    View для отображения главной страницы с постами
    Если пользователь не авторизован, ему недоступны фильтры
    """
    def get_context_data(self) -> dict:
        context = super().get_context_data()
        context['order_list'] = settings.ARTICLE_ORDER_LIST
        if self.request.user.is_authenticated:
            context['filter_list'] = settings.ARTICLE_FILTER_LIST
        return context


class UserArticleListView(LoginRequiredMixin, ArticleListBaseView):
    """
    View для вывода списка статей выбранного пользователя.
    Для собственный постов возможна фильтрация по статусу,
    чужие посты выводятся со статусом 'опубликовано'
    """
    template_name = 'articles/user_article_list.html'

    def get(self, request: HttpRequest,
            username: str = None,
            category_slug: str = None) -> HttpResponse:

        filter_by = request.GET.get('filter')
        if username != self.request.user.username or not filter_by:
            self.filter_by = 'publish'
        if filter_by == 'draft':
            self.template_name = 'articles/draft_list.html'
        return super().get(request, username, category_slug)

    def get_context_data(self) -> dict:
        context = super().get_context_data()
        if self.username == self.request.user.username:
            context['filter_list'] = settings.USER_ARTICLE_STATUS_FILTER_LIST
            context['mine'] = True
        if self.filter_by == 'publish':
            context['order_list'] = settings.ARTICLE_ORDER_LIST
        return context


class ArticleDetailView(ArticleAttrsMixin, View):
    template_name = 'articles/detail.html'
    article = None

    def dispatch(self, request, **kwargs):
        self.article = get_article_object(kwargs.get('article_id'))
        self.article = self.get_article_content_and_attrs(self.article)
        return super().dispatch(request, **kwargs)

    @query_debugger
    def get(self, request: HttpRequest, article_id: int) -> HttpResponse:
        self.change_article_views(article_id)
        form = self.get_comment_form()
        return render(request, self.template_name, self.get_context_data(form))

    def post(self, request: HttpRequest, article_id: int) -> HttpResponse:
        form = self.get_comment_form(data=request.POST,
                                     files=request.FILES)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.article = self.article
            comment.author = request.user
            comment.save()
            self.rating.incr_or_decr_rating_by_id(action='comment',
                                                  object_id=article_id)
            form = self.get_comment_form()
        return render(request, self.template_name, self.get_context_data(form))

    def get_article_content_and_attrs(self, article: Article) -> Article:
        article.content_list = get_article_render_contents(article)
        return super().get_article_content_and_attrs(article)

    @staticmethod
    def get_comment_form(**kwargs):
        form = modelform_factory(Comment, fields=['body'])
        return form(**kwargs)

    def get_context_data(self, form):
        context = {
            'article': self.article,
            'category': self.article.category,
            'form': form,
            'section': 'article'
        }
        return context


class ArticleCreateView(LoginRequiredMixin, ArticleEditMixin, CreateView):
    pass


class ArticleUpdateView(LoginRequiredMixin, ArticleEditMixin, UpdateView):
    pk_url_kwarg = 'article_id'


class ArticleDeleteView(LoginRequiredMixin, DeleteView):
    model = Article
    pk_url_kwarg = 'article_id'
    template_name = 'articles/edit/delete_form.html'

    def form_valid(self, form):
        delete_all_article_content(self.kwargs.get(self.pk_url_kwarg))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:users_article_list',
            kwargs={'username': self.request.user.username}
        )


class ArticlePreviewEditView(LoginRequiredMixin, View):
    @query_debugger
    def get(self, request: HttpRequest, article_id: int) -> HttpResponse:
        article = get_article_object(article_id)
        contents = get_article_render_contents(article)

        context = {
            'article': article,
            'contents': contents,
            'content_types': settings.ARTICLE_CONTENT_TYPES
        }
        return render(request, 'articles/edit/preview.html', context)


class ContentCreateUpdateView(LoginRequiredMixin, View):
    model = None
    content_object = None
    template_name = 'articles/content/form.html'

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
        article_id = kwargs.get('article_id')
        form = self.get_form(instance=self.content_object,
                             data=request.POST,
                             files=request.FILES)
        if form.is_valid():
            content_object = form.save()
            if not self.content_object:
                create_content(article=get_article_object(article_id),
                               content_object=content_object)
            return redirect('blog:article_edit', article_id)
        context = {
            'form': form,
            'content': self.content_object
        }
        return render(request, self.template_name, context)


class ContentDeleteView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest, article_id: int, content_id: int) -> HttpResponse:
        delete_article_content_by_id(content_id)
        return redirect('blog:article_edit', article_id)


def publish_article_view(request: HttpRequest, article_id: int) -> HttpResponse:
    publish_article(article_id)
    return redirect('blog:users_article_list', request.user.username)


class ArticleLikeView(LoginRequiredMixin, View):
    def post(self, request):
        article_id = request.POST.get('article_id')
        action = request.POST.get('action')
        if article_id and action:
            if like_article(request.user, article_id, action):
                return JsonResponse({'status': 'ok'})
        return JsonResponse({'status': ''})
