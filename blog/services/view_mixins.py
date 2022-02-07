from ..forms import PostCreationForm
from ..models import Post
from .post_rating_service import PostsRating, PostViewCounter
from account.services.decorators import query_debugger
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse_lazy


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
        self.post_view_counter.incr_view_count(post_id)
        self.rating.incr_or_decr_rating_by_id(action='view',
                                              object_id=post_id)


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
