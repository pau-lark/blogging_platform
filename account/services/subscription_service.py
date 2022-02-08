from .rating_service import UsersRating
from .users_range_service import get_user_object
from ..models import CustomUser, Subscription
from django.conf import settings
from django.db.models.query import QuerySet
import logging.config


logging.config.dictConfig(settings.LOGGING)
LOGGER = logging.getLogger('account_logger')

RATING = UsersRating()


def subscribe_user(from_user: CustomUser, to_user_username: str, action: str) -> bool:
    """
    Функция подписывает одного пользователя на другого или отписывает,
    в зависимости от значения 'action' (add/delete)
    и вызывает функцию изменения рейтинга.
    Возвращает True, в случае успеха.
    """
    to_user = get_user_object(to_user_username)
    if action == 'add':
        Subscription.objects.get_or_create(from_user=from_user,
                                           to_user=to_user)
        RATING.incr_or_decr_rating_by_id(action='add_subscriber',
                                         object_id=to_user.id)
    else:
        try:
            Subscription.objects.get(from_user=from_user,
                                     to_user=to_user).delete()
            RATING.incr_or_decr_rating_by_id(action='delete_subscriber',
                                             object_id=to_user.id)
        except Subscription.DoesNotExist:
            LOGGER.error(f'delete subscription error from {from_user} to {to_user}.'
                         f'Relation does not exist')
            return False
    return True


def get_user_subscriptions(user: CustomUser) -> QuerySet[CustomUser]:
    """Функция возвращает qs подписок, указанного пользователя"""
    return user.subscriptions.all()
