from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse


class CustomUser(AbstractUser):
    """Стандартная пользовательская модель с
    дополнительными полями"""
    photo = models.ImageField(upload_to='accounts/photos/',
                              blank=True,
                              verbose_name='Фото')
    birth_date = models.DateField(blank=True,
                                  null=True,
                                  verbose_name='Дата рождения')
    following = models.ManyToManyField('self',
                                       through='Following',
                                       related_name='followers',
                                       verbose_name='Подписки',
                                       symmetrical=False)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse('author_detail',
                       args=[
                           self.username
                       ])


class Following(models.Model):
    """Промежуточная модель для связи M2M CustomUser на себя
    с ключами пользователей и даты подписки"""
    from_user = models.ForeignKey(CustomUser,
                                  related_name='follow_from',
                                  on_delete=models.CASCADE,
                                  verbose_name='Подписчик')
    to_user = models.ForeignKey(CustomUser,
                                related_name='follow_to',
                                on_delete=models.CASCADE,
                                verbose_name='Подписка')
    follow_datatime = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-follow_datetime']

    def __str__(self):
        return f'{self.from_user} follows {self.to_user}'
