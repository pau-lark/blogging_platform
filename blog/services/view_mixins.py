from ..forms import PostCreationForm
from ..models import Post, Category
from .post_rating_service import PostsRating, PostViewCounter
from account.services.decorators import query_debugger
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404
from django.urls import reverse_lazy
import logging.config


logging.config.dictConfig(settings.LOGGING)
LOGGER = logging.getLogger('blog_logger')


class PaginatorMixin:
    paginate_by = None

    def get_paginate_list(self, object_list):
        paginator = Paginator(object_list=object_list,
                              per_page=self.paginate_by)
        page = self.request.GET.get('page')
        try:
            object_list = paginator.page(page)
        except PageNotAnInteger:
            object_list = paginator.page(1)
        except EmptyPage:
            object_list = paginator.page(paginator.num_pages)
        return object_list


class PostAttrsMixin:
    """
    Миксин для получения рейтинга, категории,
    количества просмотров, лайков и комментариев статьи
    """
    post_view_counter = PostViewCounter()
    rating = PostsRating()

    @query_debugger
    def get_post_content_and_attrs(self, article: Post) -> Post:
        article.rating = self.rating.get_rating_by_id(article.id)
        article.view_count = self.post_view_counter.get_post_view_count(article.id)
        article.users_like_count = article.users_like.count()
        article.comments_count = article.comments.count()
        return article

    def change_post_views(self, post_id: int) -> None:
        """Увеличивает количество просмотров и рейтинг статьи на 1"""
        self.post_view_counter.incr_view_count(post_id)
        self.rating.incr_or_decr_rating_by_id(action='view',
                                              object_id=post_id)

    def get_category_by_slug(self, category_slug: str) -> Category:
        try:
            return Category.objects.get(slug=category_slug)
        except Category.DoesNotExist:
            LOGGER.error(f'category {category_slug} not found')
            raise Http404(f'Категория {category_slug} не найдена')


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
