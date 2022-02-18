from .services.utils import slugify
from account.models import CustomUser
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.conf import settings
from django.urls import reverse
from django.utils import timezone


class Category(models.Model):
    title = models.CharField(max_length=200,
                             verbose_name='Наименование')
    slug = models.SlugField(max_length=200)

    class Meta:
        ordering = ['title']
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class ArticlePublishedManger(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status='published')


class Article(models.Model):
    objects = models.Manager()
    published_manager = ArticlePublishedManger()

    STATUS_CHOICES = (
        ('draft', 'Черновик'),
        ('published', 'Опубликовано')
    )

    category = models.ForeignKey(Category,
                                 on_delete=models.CASCADE,
                                 related_name='articles',
                                 verbose_name='Категория')
    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               on_delete=models.CASCADE,
                               related_name='articles',
                               verbose_name='Автор')
    title = models.CharField(max_length=200,
                             verbose_name='Название')
    slug = models.SlugField(max_length=200)
    preview_image = models.ImageField(upload_to='articles/%Y/%m/%d',
                                      verbose_name='Изображение',
                                      blank=True)
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)
    published = models.DateTimeField(null=True)
    status = models.CharField(max_length=10,
                              choices=STATUS_CHOICES,
                              default='draft')
    users_like = models.ManyToManyField(CustomUser,
                                        related_name='articles_like',
                                        verbose_name='Понравилось пользователям',
                                        blank=True)

    class Meta:
        ordering = ['-published']
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def save(self, *args, **kwargs):
        """Автоматически задает slug из title"""
        if not self.slug:
            self.slug = slugify(self.title)
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse(
            'blog:article_detail', args=[self.id]
        )


class Content(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE,
                                related_name='contents',
                                verbose_name='Статья')
    content_type = models.ForeignKey(ContentType,
                                     on_delete=models.CASCADE,
                                     limit_choices_to={
                                         'model__in': (
                                             'text',
                                             'image',
                                             'video'
                                         )
                                     })
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name = 'Контент'
        verbose_name_plural = 'Контент'

    def __str__(self):
        return f'{self.article.title} - {self._meta.model_name}'


class ModelNameMixin:
    def get_model_name(self):
        return self._meta.model_name


class Text(ModelNameMixin, models.Model):
    text = models.TextField(verbose_name='Текст')

    class Meta:
        verbose_name = 'Текст статьи'
        verbose_name_plural = 'Тексты статьи'


class Image(ModelNameMixin, models.Model):
    image = models.ImageField(upload_to='articles/%Y/%m/%d',
                              verbose_name='Изображение')

    class Meta:
        verbose_name = 'Картинка статьи'
        verbose_name_plural = 'Картинки статьи'


class Video(ModelNameMixin, models.Model):
    url = models.URLField(verbose_name='URL видео')

    class Meta:
        verbose_name = 'Видео статьи'
        verbose_name_plural = 'Видео статьи'


class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE,
                                related_name='comments',
                                verbose_name='Статья')
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
                               related_name='comments',
                               verbose_name='Автор комментария')
    body = models.TextField(verbose_name='Текст комментария')
    created = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return f'Comment by {self.author}'
