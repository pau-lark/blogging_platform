from django.conf import settings
from django.utils.text import slugify as django_slugify


def slugify(string):
    """
    Переопределяет django_slugify,
    чтобы можно было использовать кириллицу
    """
    return django_slugify(''.join(settings.ALPHABET.get(w, w) for w in string.lower()))
