from ..models import CustomUser
from .rating_service import UsersRating
from django.conf import settings
from django.db.models.query import QuerySet
from django.db.models import Count
from django.http import Http404
import logging.config


logging.config.dictConfig(settings.LOGGING)
LOGGER = logging.getLogger('account_logger')


def get_user_object(username: str) -> CustomUser:
    """Получаем пользователя по имени"""
    try:
        user = CustomUser.objects.get(username=username)
    except CustomUser.DoesNotExist:
        LOGGER.error(f'User {username} not found')
        raise Http404(f'Пользователь {username} не найден')
    return user


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
        return user.subscriptions.prefetch_related('articles').all()
    elif filter_by == 'subscribers':
        user = get_user_object(username)
        return user.subscribers.prefetch_related('articles').all()
    return CustomUser.objects.prefetch_related('articles').exclude(username=username)


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
        LOGGER.warning(f'Rating sort error of user list {user_list}. Some users have not rating')
    return user_list


def _get_order_by_article_count(user_list: QuerySet[CustomUser]) -> QuerySet[CustomUser]:
    """Возвращает список пользователей, отсортированный по количеству постов"""
    return user_list.annotate(articles_count=Count('articles')).order_by('-articles_count')


def _get_sorted_user_list(user_list: QuerySet[CustomUser], order_by: str):
    """
    Получаем отсортированный qs пользователей
    Значения order_by:
        'rating' - сортировать по рейтингу;
        'article_count' - сортировать по количеству постов.
    """
    if order_by == 'rating':
        return _get_order_by_rating(user_list)
    elif order_by == 'article_count':
        return _get_order_by_article_count(user_list)


def get_filtered_and_sorted_user_list(
        username: str,
        filter_by: str = 'all',
        order_by: str = 'rating') -> QuerySet[CustomUser]:
    """Вызывает функции фильтрации и сортировки пользователей"""
    users = get_filtered_user_list(username, filter_by)
    return _get_sorted_user_list(users, order_by)
