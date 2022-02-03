# Generated by Django 4.0.1 on 2022-02-03 11:34

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0009_alter_post_options_post_poster_alter_post_published'),
    ]

    operations = [
        migrations.RenameField(
            model_name='post',
            old_name='poster',
            new_name='preview_image',
        ),
        migrations.AlterField(
            model_name='post',
            name='published',
            field=models.DateTimeField(default=datetime.datetime(2022, 2, 3, 11, 34, 10, 833001, tzinfo=utc)),
        ),
    ]