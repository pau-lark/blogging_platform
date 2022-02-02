from account.services.rating_service import RatingBase, REDIS
from django.conf import settings


class PostsRating(RatingBase):
    """Класс для подсчёта рейтинга постов"""
    rating_by_action = settings.POST_RATING_BY_ACTION
    redis_key = 'post_rating'


class PostViewCounter:
    """Класс для подсчёта количества постов"""
    @staticmethod
    def _get_post_key(post_id: int) -> str:
        """Получение ключа по id поста"""
        return f'post:{post_id}:id'

    def incr_view_count(self, post_id: int) -> None:
        """Увеличение количества просмотров на 1"""
        REDIS.incr(self._get_post_key(post_id))

    def get_post_view_count(self, post_id: int) -> int:
        """Получение количества просмотров поста"""
        view_count = REDIS.get(self._get_post_key(post_id))
        if not view_count:
            return 0
        return int(view_count)
