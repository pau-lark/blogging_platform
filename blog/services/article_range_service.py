from ..models import Article
from .article_rating_service import ArticlesRating
from account.services.decorators import query_debugger
from account.services.users_range_service import get_filtered_user_list
from django.conf import settings
from django.db.models.query import QuerySet
from django.http import Http404
import logging.config


logging.config.dictConfig(settings.LOGGING)
LOGGER = logging.getLogger('blog_logger')


@query_debugger
def get_article_object(article_id: int) -> Article:
    """Получаем пост по id"""
    try:
        article = Article.objects.get(id=article_id)
    except Article.DoesNotExist:
        LOGGER.error(f'article {article_id} not found')
        raise Http404(f'Пост {article_id} не найден')
    return article


@query_debugger
def get_article_list_by_category(category_slug: str) -> QuerySet[Article]:
    """
    Возвращает qs постов по категории.
    Если категория не задана, возвращает все посты
    """
    if category_slug:
        return Article.published_manager.prefetch_related('users_like', 'comments')\
            .filter(category__slug=category_slug)
    return Article.published_manager.prefetch_related('users_like', 'comments').all()


@query_debugger
def _get_filtered_article_list(username: str, category_slug: str, filter_by: str) -> QuerySet[Article]:
    """
    Получаем qs статей, в зависимости от категории и фильтра
    Значения filter_by:
        'subscriptions' - фильтровать по подпискам;
        'all' - все статьи;
        'publish' - все опубликованные статьи конкретного пользователя;
        'draft' - свои черновики.
    """
    articles = get_article_list_by_category(category_slug)
    if username:
        if filter_by == 'subscriptions':
            subscription_user_list = get_filtered_user_list(username, filter_by)
            return articles.filter(author__in=subscription_user_list)
        elif filter_by == 'publish':
            return articles.filter(author__username=username)
        elif filter_by == 'draft':
            return Article.objects.filter(author__username=username, status='draft')
        elif filter_by == 'all':
            return articles.exclude(author__username=username)
    return articles


def _get_order_by_rating(article_list: QuerySet[Article]) -> list:
    """Возвращает список постов, отсортированный по рейтингу"""
    article_list = list(article_list)
    rating = ArticlesRating()
    articles_sorted_by_rating_ids = [
        int(article_id) for article_id in rating.get_range_list_by_rating()
    ]
    try:
        article_list.sort(
            key=lambda article: articles_sorted_by_rating_ids.index(article.id)
        )
    except ValueError:
        LOGGER.error(f'Rating sort error of article list {article_list}. Some articles have not rating')
    return article_list


def _get_order_by_date(article_list: QuerySet[Article]) -> QuerySet[Article]:
    """Возвращает список постов, отсортированный по дате"""
    return article_list.order_by('-published')


@query_debugger
def _get_sorted_article_list(article_list: QuerySet[Article], order_by: str):
    """
    Получаем отсортированный qs постов
    Значения order_by:
        'rating' - сортировать по рейтингу;
        'date' - сортировать по date.
    """
    if order_by == 'rating':
        return _get_order_by_rating(article_list)
    # во всех остальных случаях - по дате
    return _get_order_by_date(article_list)


def get_filtered_and_sorted_article_list(
        username: str,
        category_slug: str,
        filter_by: str = 'all',
        order_by: str = 'rating') -> QuerySet[Article]:
    """Вызывает функции фильтрации и сортировки постов"""
    articles = _get_filtered_article_list(username, category_slug, filter_by)
    return _get_sorted_article_list(articles, order_by)
