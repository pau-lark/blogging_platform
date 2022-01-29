from django.conf import settings
import redis


class ChangeRatingError(Exception):
    pass


REDIS = redis.StrictRedis(host=settings.REDIS_HOST,
                          port=settings.REDIS_PORT,
                          db=settings.REDIS_DB)


class RatingBase:
    """Базовый класс для подсчёта рейтинга постов и пользователей"""

    key = None

    def get_rating_by_key(self, object_id: int) -> str:
        """Получение рейтинга объекта по ключу"""
        return REDIS.zscore(name=self.key,
                            value=object_id)

    def get_range_list_by_rating(self) -> list:
        """Получение отсортированного списка по рейтингу"""
        return REDIS.zrange(name=self.key,
                            start=0,
                            end=-1,
                            desc=True)

    def incr_or_decr_rating_by_key(self, increment: int, object_id: int) -> None:
        """Изменение рейтинга объекта"""
        REDIS.zincrby(name=self.key,
                      amount=increment,
                      value=object_id)

    def clear_rating_by_key(self, object_id: int) -> None:
        """Очистка рейтинг объекта"""
        REDIS.zrem(self.key, object_id)


class UsersRating(RatingBase):
    """Класс для подсчёта рейтинга пользователей"""
    rating_by_action = {
        'add_subscriber': 10,
        'delete_subscriber': -10,
        'create_post': 25,
        'delete_post': -25
    }
    key = 'user_rating'

    def incr_or_decr_rating_by_key(self, action: str, object_id: int) -> None:
        if action in self.rating_by_action:
            super().incr_or_decr_rating_by_key(self.rating_by_action[action],
                                               object_id)
        # и пишем в лог
        raise ChangeRatingError('Action does not exist')


class PostsRating(RatingBase):
    """Класс для подсчёта рейтинга постов"""
    rating_by_action = {
        'view': 1,
        'like': 3,
        'unlike': -3,
        'comment': 5
    }
    key = 'post_rating'

    def incr_or_decr_rating_by_key(self, action: str, object_id: int) -> None:
        if action in self.rating_by_action:
            super().incr_or_decr_rating_by_key(self.rating_by_action[action],
                                               object_id)
        # и пишем в лог
        raise ChangeRatingError('Action does not exist')


class PostViewCounter:
    """Класс для подсчёта количества постов"""
    @staticmethod
    def _get_post_key(post_id):
        return f'post:{post_id}:id'

    def add_view_count(self, post_id):
        REDIS.incr(self._get_post_key(post_id))

    def get_post_view_count(self, post_id):
        return REDIS.get(self._get_post_key(post_id))
