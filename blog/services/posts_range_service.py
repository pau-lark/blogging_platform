from ..models import Post, Category
from .post_rating_service import PostsRating
from account.services.decorators import query_debugger
from account.services.users_range_service import get_filtered_user_list
from django.db.models.query import QuerySet
from django.http import Http404
from django.shortcuts import get_object_or_404


@query_debugger
def get_category_by_slug(category_slug: str) -> Category:
    """Получаем категорию по слагу"""
    try:
        category = get_object_or_404(Category,
                                     slug=category_slug)
        return category
    except Category.DoesNotExist:
        # TODO: и пишем в лог
        raise Http404(f'Категория {category_slug} не найдена')


@query_debugger
def get_post_object(post_id: int) -> Post:
    """Получаем пост по id"""
    try:
        post = get_object_or_404(Post, id=post_id)
    except Post.DoesNotExist:
        # TODO: и пишем в лог
        raise Http404(f'Пост {post_id} не найден')
    return post


@query_debugger
def get_post_list_by_category(category_slug: str) -> QuerySet[Post]:
    """
    Возвращает qs постов по категории.
    Если категория не задана, возвращает все посты
    """
    # TODO: добавить prefetch_related с комментами(наверное)
    if category_slug:
        return Post.published_manager.filter(category__slug=category_slug)
    return Post.published_manager.all()


@query_debugger
def _get_filtered_post_list(username: str, category_slug: str, filter_by: str) -> QuerySet[Post]:
    """
    Получаем qs статей, в зависимости от категории и фильтра
    Значения filter_by:
        'subscriptions' - фильтровать по подпискам;
        'all' - все статьи;
        'user' - все статьи конкретного пользователя.
    """
    posts = get_post_list_by_category(category_slug)
    print(posts)
    if username:
        if filter_by == 'subscriptions':
            subscription_user_list = get_filtered_user_list(username, filter_by)
            return posts.filter(author__in=subscription_user_list)
        elif filter_by == 'user':
            return posts.filter(author__username=username)
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
    print(posts_sorted_by_rating_ids)
    try:
        post_list.sort(
            key=lambda post: posts_sorted_by_rating_ids.index(post.id)
        )
    except ValueError as e:
        # в лог
        pass
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
    if order_by == 'date':
        return _get_order_by_date(post_list)
    # во всех остальных случаях - по рейтингу
    return _get_order_by_rating(post_list)


def get_filtered_and_sorted_post_list(
        username: str,
        category_slug: str,
        filter_by: str = 'all',
        order_by: str = 'rating') -> QuerySet[Post]:
    """Вызывает функции фильтрации и сортировки постов"""
    posts = _get_filtered_post_list(username, category_slug, filter_by)
    return _get_sorted_post_list(posts, order_by)
