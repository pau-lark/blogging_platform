# Generated by Django 4.0.1 on 2022-01-25 13:20

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0005_alter_post_managers_alter_post_published'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='published',
            field=models.DateTimeField(default=datetime.datetime(2022, 1, 25, 13, 20, 13, 583729, tzinfo=utc)),
        ),
    ]
