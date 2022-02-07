from account.services.rating_service import RatingBase, REDIS
from django.conf import settings


class ArticlesRating(RatingBase):
    """Класс для подсчёта рейтинга постов"""
    rating_by_action = settings.ARTICLE_RATING_BY_ACTION
    redis_key = 'article_rating'


class ArticleViewCounter:
    """Класс для подсчёта количества постов"""
    @staticmethod
    def _get_article_key(article_id: int) -> str:
        """Получение ключа по id поста"""
        return f'article:{article_id}:id'

    def incr_view_count(self, article_id: int) -> None:
        """Увеличение количества просмотров на 1"""
        REDIS.incr(self._get_article_key(article_id))

    def get_article_view_count(self, article_id: int) -> int:
        """Получение количества просмотров поста"""
        view_count = REDIS.get(self._get_article_key(article_id))
        if not view_count:
            return 0
        return int(view_count)
