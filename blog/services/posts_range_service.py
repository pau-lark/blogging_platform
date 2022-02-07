from ..models import Post
from .post_rating_service import PostsRating
from account.services.decorators import query_debugger
from account.services.users_range_service import get_filtered_user_list
from django.conf import settings
from django.db.models.query import QuerySet
from django.http import Http404
import logging.config


logging.config.dictConfig(settings.LOGGING)
LOGGER = logging.getLogger('blog_logger')


@query_debugger
def get_post_object(post_id: int) -> Post:
    """Получаем пост по id"""
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        LOGGER.error(f'post {post_id} not found')
        raise Http404(f'Пост {post_id} не найден')
    return post


@query_debugger
def get_post_list_by_category(category_slug: str) -> QuerySet[Post]:
    """
    Возвращает qs постов по категории.
    Если категория не задана, возвращает все посты
    """
    if category_slug:
        return Post.published_manager.prefetch_related('users_like', 'comments')\
            .filter(category__slug=category_slug)
    return Post.published_manager.prefetch_related('users_like', 'comments').all()


@query_debugger
def _get_filtered_post_list(username: str, category_slug: str, filter_by: str) -> QuerySet[Post]:
    """
    Получаем qs статей, в зависимости от категории и фильтра
    Значения filter_by:
        'subscriptions' - фильтровать по подпискам;
        'all' - все статьи;
        'publish' - все опубликованные статьи конкретного пользователя;
        'draft' - свои черновики.
    """
    posts = get_post_list_by_category(category_slug)
    if username:
        if filter_by == 'subscriptions':
            subscription_user_list = get_filtered_user_list(username, filter_by)
            return posts.filter(author__in=subscription_user_list)
        elif filter_by == 'publish':
            return posts.filter(author__username=username)
        elif filter_by == 'draft':
            return Post.objects.filter(author__username=username, status='draft')
        elif filter_by == 'all':
            return posts.exclude(author__username=username)
    return posts


def _get_order_by_rating(post_list: QuerySet[Post]) -> list:
    """Возвращает список постов, отсортированный по рейтингу"""
    post_list = list(post_list)
    rating = PostsRating()
    posts_sorted_by_rating_ids = [
        int(post_id) for post_id in rating.get_range_list_by_rating()
    ]
    try:
        post_list.sort(
            key=lambda post: posts_sorted_by_rating_ids.index(post.id)
        )
    except ValueError:
        LOGGER.error(f'Rating sort error of post list {post_list}. Some posts have not rating')
    return post_list


def _get_order_by_date(post_list: QuerySet[Post]) -> QuerySet[Post]:
    """Возвращает список постов, отсортированный по дате"""
    return post_list.order_by('-published')


@query_debugger
def _get_sorted_post_list(post_list: QuerySet[Post], order_by: str):
    """
    Получаем отсортированный qs постов
    Значения order_by:
        'rating' - сортировать по рейтингу;
        'date' - сортировать по date.
    """
    if order_by == 'rating':
        return _get_order_by_rating(post_list)
    # во всех остальных случаях - по дате
    return _get_order_by_date(post_list)


def get_filtered_and_sorted_post_list(
        username: str,
        category_slug: str,
        filter_by: str = 'all',
        order_by: str = 'rating') -> QuerySet[Post]:
    """Вызывает функции фильтрации и сортировки постов"""
    posts = _get_filtered_post_list(username, category_slug, filter_by)
    return _get_sorted_post_list(posts, order_by)
