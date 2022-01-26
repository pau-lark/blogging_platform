from ..models import CustomUser
from django.shortcuts import get_object_or_404


# Может в ООП?
def get_filtered_user_list(username: str, filter_by: str = None) -> CustomUser:
    """Получаем qs пользователей, в зависимости от фильтра"""
    user = get_object_or_404(CustomUser, username=username)
    if filter_by == 'subscriptions':
        return user.subscriptions.all()
    elif filter_by == 'subscribers':
        return user.subscribers.all()
    return CustomUser.objects.exclude(username=username)


def get_sorted_user_list(user_list: CustomUser, order_by: str = None) -> CustomUser:
    pass
