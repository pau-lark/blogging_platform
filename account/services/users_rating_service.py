from django.conf import settings
import redis


class ChangeRatingError(Exception):
    pass


REDIS = redis.StrictRedis(host=settings.REDIS_HOST,
                          port=settings.REDIS_PORT,
                          db=settings.REDIS_DB)


class RatingMixin:
    """Миксин для подсчёта рейтинга постов и пользователей"""
    key = None
    rating_by_action = None

    def get_rating_by_id(self, object_id: int) -> str:
        """Получение рейтинга объекта по id"""
        return REDIS.zscore(name=self.key,
                            value=object_id)

    def get_range_list_by_rating(self) -> list:
        """Получение отсортированного списка по рейтингу"""
        return REDIS.zrange(name=self.key,
                            start=0,
                            end=-1,
                            desc=True)

    def incr_or_decr_rating_by_id(self, action: str, object_id: int) -> None:
        """Изменение рейтинга объекта"""
        if action in self.rating_by_action:
            REDIS.zincrby(name=self.key,
                          amount=self.rating_by_action(action),
                          value=object_id)
        else:
            # и пишем в лог
            raise ChangeRatingError('Action does not exist')

    def clear_rating_by_id(self, object_id: int) -> None:
        """Очистка рейтинг объекта"""
        REDIS.zrem(self.key, object_id)


class UsersRating(RatingMixin):
    """Класс для подсчёта рейтинга пользователей"""
    rating_by_action = settings.USER_RATING_BY_ACTION
    key = 'user_rating'


class PostsRating(RatingMixin):
    """Класс для подсчёта рейтинга постов"""
    rating_by_action = settings.POST_RATING_BY_ACTION
    key = 'post_rating'


class PostViewCounter:
    """Класс для подсчёта количества постов"""
    @staticmethod
    def _get_post_key(post_id):
        """Получение ключа по id поста"""
        return f'post:{post_id}:id'

    def incr_view_count(self, post_id):
        """Увеличение количества просмотров на 1"""
        REDIS.incr(self._get_post_key(post_id))

    def get_post_view_count(self, post_id):
        """Получение количества просмотров"""
        return REDIS.get(self._get_post_key(post_id))
