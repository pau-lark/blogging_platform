# Generated by Django 4.0.1 on 2022-01-18 19:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_alter_content_options_alter_content_content_type'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='content',
            options={'verbose_name': 'Контент', 'verbose_name_plural': 'Контент'},
        ),
    ]
