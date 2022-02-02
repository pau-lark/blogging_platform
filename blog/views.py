from .forms import SearchForm
from .models import Post, Category
from .services.post_content_service import \
    get_text_preview_for_post,\
    get_post_content
from .services.posts_range_service import \
    get_filtered_and_sorted_post_list,\
    get_category_by_slug,\
    get_post_object
from .services.post_rating_service import PostsRating, PostViewCounter
from account.services.decorators import query_debugger
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.generic.base import View
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string


RATING = PostsRating()


def index(request):
    form = SearchForm()
    return render(request, 'base.html', {'search_form': form})


# TODO: пагинация
class PostListView(View):
    category = None
    post_view_counter = PostViewCounter()

    @query_debugger
    def get(self, request: HttpRequest,
            username: str = None,
            category_slug: str = None) -> HttpResponse:
        """
        Функция для вывода фильтрованного списка статей для
        авторизованного пользователя
        и списка всех статей для неавторизованного.
        Также производится сортировка и фильтрация по категориям.
        К каждой статье добавляется превью, рейтинг,
        количество лайков и просмотров
        """
        filter_by = request.GET.get('filter')
        order_by = request.GET.get('order')
        if not username and request.user.is_authenticated:
            username = request.user.username

        posts = get_filtered_and_sorted_post_list(username,
                                                  category_slug,
                                                  filter_by,
                                                  order_by)
        if category_slug:
            self.category = get_category_by_slug(category_slug)

        for post in posts:
            post.preview_content = get_text_preview_for_post(post)
            post.rating = RATING.get_rating_by_id(post.id)
            post.view_count = self.post_view_counter.get_post_view_count(post.id)
            # TODO: comments
            post.comments_count = 0

        context = {
            'posts': posts,
            'category': self.category,
            'username': username,
            'section': 'post',
            'filter': filter_by,
            'order': order_by
        }
        return render(request, 'posts/list.html', context)


# вариант 2
@query_debugger
def post_list_view(request, category_slug=None):
    if category_slug:
        posts = Post.published_manager.\
            filter(category__slug=category_slug)
        category = get_object_or_404(Category,
                                     slug=category_slug)
    else:
        posts = Post.published_manager.all()
        category = None
    for post in posts:
        preview_content = post.contents.filter(content_type__model='text').first()
        preview_content = preview_content.content_object
        post.preview_content = preview_content.text

    return render(request, 'posts/list.html',
                  {'object_list': posts,
                   'section': 'post',
                   'category': category})


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


@query_debugger
def post_detail_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    contents = []
    # prefetch ускоряет ~ с 0.09 до 0.08, возможно, принципиально на жирных постах
    for content in post.contents.all():
        content_object = content.content_object
        model_name = content.content_type.model
        content_template_response = render_to_string(f'posts/content/{model_name}.html',
                                                     {'content_object': content_object})
        contents.append(content_template_response)

        post.rating = RATING.get_rating_by_id(post.id)
    context = {
        'post': post,
        'contents': contents,
        'section': 'post'
    }
    return render(request, 'posts/detail.html', context)
