from ..models import Article
from .article_rating_service import ArticlesRating
from .article_range_service import get_article_object
from django.conf import settings
import logging.config


logging.config.dictConfig(settings.LOGGING)
LOGGER = logging.getLogger('blog_logger')

RATING = ArticlesRating()


def like_article(user, article_id: int, action: str) -> bool:
    """
    Функция ставит или убирает лайк статье
    в зависимости от значения 'action' (like/unlike)
    и вызывает функцию изменения рейтинга.
    Возвращает True, в случае успеха.
    """
    try:
        article = get_article_object(int(article_id))
        if action == 'like':
            article.users_like.add(user)
            RATING.incr_or_decr_rating_by_id(action='like',
                                             object_id=article_id)
        else:
            article.users_like.remove(user)
            RATING.incr_or_decr_rating_by_id(action='unlike',
                                             object_id=article_id)
        return True
    except Article.DoesNotExist:
        LOGGER.error(f'like/unlike error, article {article_id} not found')
        return False
