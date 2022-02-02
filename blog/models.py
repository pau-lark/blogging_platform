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


class PostPublishedManger(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status='published')


class Post(models.Model):
    published_manager = PostPublishedManger()
    objects = models.Manager()

    STATUS_CHOICES = (
        ('draft', 'Черновик'),
        ('published', 'Опубликовано')
    )

    category = models.ForeignKey(Category,
                                 on_delete=models.CASCADE,
                                 related_name='posts',
                                 verbose_name='Категория')
    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               on_delete=models.CASCADE,
                               related_name='posts',
                               verbose_name='Автор')
    title = models.CharField(max_length=200,
                             verbose_name='Название')
    slug = models.SlugField(max_length=200)
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)
    published = models.DateTimeField(default=timezone.now())
    status = models.CharField(max_length=10,
                              choices=STATUS_CHOICES,
                              default='draft')

    class Meta:
        ordering = ['-published']
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse(
            'blog:post_detail', args=[self.id]
        )

    # Менеджер?
    def get_first_text_content(self):
        content = self.contents.filter(content_type__model='text').first()
        return content.content_object.text


class Content(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             related_name='contents',
                             verbose_name='Пост')
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
        return f'{self.post.title} - {self._meta.model_name}'


class Text(models.Model):
    text = models.TextField(verbose_name='Текст')


class Image(models.Model):
    image = models.ImageField(upload_to='posts/%Y/%m/%d',
                              verbose_name='Изображение')


class Video(models.Model):
    url = models.URLField(verbose_name='URL видео')
