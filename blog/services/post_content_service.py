from ..models import Post, Content, Text, Image, Video
from .posts_range_service import get_post_object
from account.services.rating_service import UsersRating
from account.services.decorators import query_debugger
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.http import Http404
from django.template.loader import render_to_string
from typing import Union
import logging.config


RATING = UsersRating()

logging.config.dictConfig(settings.LOGGING)
LOGGER = logging.getLogger('blog_logger')


def get_text_preview_for_post(post: Post) -> str:
    """Функция возвращает текстовое превью статьи или пустую строку"""
    preview_content = post.contents.filter(content_type__model='text').first()
    try:
        return preview_content.content_object.text
    except AttributeError:
        LOGGER.error(f'post {post.id}, content {preview_content.id}, text not found')
        return ''


def delete_post_content_by_id(content_id: int) -> None:
    """Функция удаляет контент и его содержание"""
    try:
        content = Content.objects.get(id=content_id)
    except Content.DoesNotExist:
        LOGGER.error(f'content {content_id} not found')
        raise Http404(f'Контент {content_id} не найден')
    content.content_object.delete()
    content.delete()


@query_debugger
def get_post_render_contents(post: Post) -> list[tuple]:
    """
    Функция генерирует шаблон для каждого контент-объекта статьи,
    возвращает список кортежей.
    В кортеж входят SafeString и объект контента
    """
    contents = []
    for content in post.contents.prefetch_related('content_object').all():
        content_object = content.content_object
        if content_object:
            model_name = content_object.get_model_name()
            content_template_response = render_to_string(f'posts/content/{model_name}.html',
                                                         {'content_object': content_object})
            contents.append((content_template_response, content))
    return contents


def get_model_by_name(model_name: str) -> Union[Text, Image, Video, None]:
    """Возвращает модель одного из типов контента (Text, Image, Video)"""
    if model_name in settings.POST_CONTENT_TYPES:
        try:
            return ContentType.objects.get(app_label='blog',
                                           model=model_name).model_class()
        except ContentType.DoesNotExist:
            LOGGER.error(f'model {model_name} not found')
            return None
    LOGGER.error(f'unknown model {model_name}')
    return None


def get_content_object_by_model_name_and_id(
        model_name: str,
        content_object_id: int) -> Union[Text, Image, Video]:

    model = get_model_by_name(model_name)
    if model:
        try:
            return model.objects.get(id=content_object_id)
        except model.DoesNotExist:
            LOGGER.error(f'{model_name} {content_object_id} not found')
            raise Http404(f'Контент {content_object_id} не найден')
    raise Http404(f'Контент {content_object_id} не найден: unknown model {model_name}')


def create_content(post: Post, content_object: Union[Text, Image, Video]) -> None:
    try:
        Content.objects.create(post=post, content_object=content_object)
    except Exception as e:
        LOGGER.warning(f'create content error', e)


def delete_all_post_content(post_id: int) -> None:
    """Удаляет содержимое статьи и чистит её рейтинг"""
    post = get_post_object(post_id)
    for content in post.contents.all():
        content.content_object.delete()
    RATING.incr_or_decr_rating_by_id(action='delete_post',
                                     object_id=post.author.id)
    RATING.clear_rating_by_id(object_id=post_id)


def publish_post(post_id: int) -> None:
    """Меняет статус статьи на "опубликовано", добавляет рейтинг пользователю"""
    post = get_post_object(post_id)
    post.status = 'published'
    post.save()
    RATING.incr_or_decr_rating_by_id(action='create_post',
                                     object_id=post.author.id)
