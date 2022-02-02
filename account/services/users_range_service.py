from ..models import CustomUser
from .decorators import query_debugger
from .rating_service import UsersRating
from django.db.models.query import QuerySet
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404


@query_debugger
def get_user_object(username: str) -> CustomUser:
    """Получаем пользователя по имени"""
    try:
        user = get_object_or_404(CustomUser, username=username)
    except CustomUser.DoesNotExist:
        # TODO: и пишем в лог
        raise Http404(f'Пользователь {username} не найден')
    return user


@query_debugger
def get_filtered_user_list(username: str, filter_by: str) -> QuerySet[CustomUser]:
    """
    Получаем qs пользователей, в зависимости от фильтра
    Значения filter_by:
        'subscriptions' - фильтровать по подпискам;
        'subscribers' - фильтровать по подписчикам;
        'all' - все пользователи.
    """
    if filter_by == 'subscriptions':
        user = get_user_object(username)
        return user.subscriptions.prefetch_related('posts').all()
    elif filter_by == 'subscribers':
        user = get_user_object(username)
        return user.subscribers.prefetch_related('posts').all()
    return CustomUser.objects.prefetch_related('posts').exclude(username=username)


def _get_order_by_rating(user_list: QuerySet[CustomUser]) -> list:
    """Возвращает список пользователей, отсортированный по рейтингу"""
    user_list = list(user_list)
    rating = UsersRating()
    users_sorted_by_rating_ids = [
        int(user_id) for user_id in rating.get_range_list_by_rating()
    ]
    try:
        user_list.sort(
            key=lambda user: users_sorted_by_rating_ids.index(user.id)
        )
    except ValueError as e:
        # в лог
        pass
    return user_list


def _get_order_by_post_count(user_list: QuerySet[CustomUser]) -> QuerySet[CustomUser]:
    """Возвращает список пользователей, отсортированный по количеству постов"""
    return user_list.annotate(posts_count=Count('posts')).order_by('-posts_count')


@query_debugger
def _get_sorted_user_list(user_list: QuerySet[CustomUser], order_by: str):
    """
    Получаем отсортированный qs пользователей
    Значения order_by:
        'rating' - сортировать по рейтингу;
        'post_count' - сортировать по количеству постов.
    """
    if order_by == 'rating':
        return _get_order_by_rating(user_list)
    elif order_by == 'post_count':
        return _get_order_by_post_count(user_list)


def get_filtered_and_sorted_user_list(
        username: str,
        filter_by: str = 'all',
        order_by: str = 'rating') -> QuerySet[CustomUser]:
    """Вызывает функции фильтрации и сортировки пользователей"""
    users = get_filtered_user_list(username, filter_by)
    return _get_sorted_user_list(users, order_by)
