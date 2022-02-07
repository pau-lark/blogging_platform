from ..models import Article
from .article_rating_service import ArticlesRating
from .article_range_service import get_article_object


RATING = ArticlesRating()


def like_article(user, article_id: int, action: str) -> bool:
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
        # TODO: в лог
        return False
