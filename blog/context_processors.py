from .models import Category


def category(request):
    return {'categories': Category.objects.all()}


def previous_page(request):
    return {'previous_page': request.META['HTTP_REFERER']}
