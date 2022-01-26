from ..models import CustomUser
from django.shortcuts import get_object_or_404
from django.db.models.query import QuerySet
from django.db.models import Count


# Может в ООП?
def get_filtered_user_list(username: str, filter_by: str = 'all') -> QuerySet[CustomUser]:
    """Получаем qs пользователей, в зависимости от фильтра"""
    user = get_object_or_404(CustomUser, username=username)
    if filter_by == 'subscriptions':
        return user.subscriptions.all()
    elif filter_by == 'subscribers':
        return user.subscribers.all()
    return CustomUser.objects.exclude(username=username)


# rating = UserRating()


# def _get_order_by_rating(user_list: QuerySet[CustomUser]) -> list:
#     """Возвращает список пользователей, отсортированный по рейтингу"""
#     user_list = list(user_list)
#     users_sorted_by_rating_ids = rating.get_users_sorted_by_rating()
#     user_list.sort(
#         key=lambda user: users_sorted_by_rating_ids.index(user.id)
#     )
#     return user_list


def _get_order_by_popularity(user_list: QuerySet[CustomUser]) -> QuerySet[CustomUser]:
    """Возвращает список пользователей,
    отсортированный по количеству подписчиков"""
    return user_list.annotate(subscribers_count=Count('subscribers'))\
        .order_by('-subscribers_count')


def _get_order_by_post_count(user_list: QuerySet[CustomUser]) -> QuerySet[CustomUser]:
    """Возвращает список пользователей,
        отсортированный по количеству постов"""
    return user_list.annotate(posts_count=Count('posts')).order_by('-posts_count')


def get_sorted_user_list(user_list: QuerySet[CustomUser], order_by: str = 'rating'):
    print(user_list, order_by)
    order_by_chose = {
        #'rating': _get_order_by_rating(user_list),
        'subscribers': _get_order_by_popularity(user_list),
        'post_count': _get_order_by_post_count(user_list)
    }
    return order_by_chose.get(order_by)


"""
if order_by == 'rating':
    pass
elif order_by == 'popularity':
    pass
elif order_by == 'post_count':
    pass
"""
