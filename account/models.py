from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse


class CustomUser(AbstractUser):
    """
    Стандартная пользовательская модель с
    дополнительными полями
    """
    photo = models.ImageField(upload_to='accounts/photos/',
                              blank=True,
                              verbose_name='Фото')
    birth_date = models.DateField(blank=True,
                                  null=True,
                                  verbose_name='Дата рождения')
    about = models.TextField(blank=True,
                             null=True,
                             verbose_name='О себе')
    subscriptions = models.ManyToManyField('self',
                                           through='Subscription',
                                           related_name='subscribers',
                                           verbose_name='Подписки',
                                           symmetrical=False)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse('user_profile',
                       args=[
                           self.username
                       ])


class Subscription(models.Model):
    """
    Промежуточная модель для связи M2M CustomUser на себя
    с ключами пользователей и даты подписки
    """
    from_user = models.ForeignKey(CustomUser,
                                  on_delete=models.CASCADE,
                                  related_name='subscribed_users',
                                  verbose_name='Подписчик')
    to_user = models.ForeignKey(CustomUser,
                                on_delete=models.CASCADE,
                                related_name='subscripted_users',
                                verbose_name='Подписка')
    subscription_datatime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.from_user} subscribed {self.to_user}'
