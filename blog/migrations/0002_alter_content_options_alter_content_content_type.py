# Generated by Django 4.0.1 on 2022-01-18 16:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='content',
            options={'verbose_name': 'Контент'},
        ),
        migrations.AlterField(
            model_name='content',
            name='content_type',
            field=models.ForeignKey(limit_choices_to={'model__in': ('text', 'image', 'video')}, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype'),
        ),
    ]
