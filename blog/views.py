from django.shortcuts import render, get_object_or_404
from .forms import SearchForm
from django.views.generic import ListView, DetailView
from .models import Post, Category
from django.template.loader import render_to_string

from .common.decorators import query_debugger


def index(request):
    form = SearchForm()
    return render(request, 'base.html', {'search_form': form})


class PostListView(ListView):
    model = Post
    template_name = 'posts/list.html'


# вариант 2
@query_debugger
def post_list_view(request, category_slug=None):
    if category_slug:
        posts = Post.published_manager.\
            filter(category__slug=category_slug)
        category = get_object_or_404(Category,
                                     slug=category_slug)
    else:
        posts = Post.published_manager.all()
        category = None
    for post in posts:
        preview_content = post.contents.filter(content_type__model='text').first()
        preview_content = preview_content.content_object
        post.preview_content = preview_content.text

    return render(request, 'posts/list.html',
                  {'object_list': posts,
                   'section': 'post',
                   'category': category})


@query_debugger
def post_detail_view(request, **kwargs):
    year, month, day, slug = kwargs.values()
    post = get_object_or_404(Post,
                             created__year=year,
                             created__month=month,
                             created__day=day,
                             slug=slug)
    contents = []
    # prefetch ускоряет ~ с 0.09 до 0.08, возможно, принципиально на жирных постах
    for content in post.contents.all():
        content_object = content.content_object
        model_name = content.content_type.model
        content_template_response = render_to_string(f'posts/content/{model_name}.html',
                                                     {'content_object': content_object})
        contents.append(content_template_response)
    context = {
        'post': post,
        'contents': contents,
        'section': 'post'
    }
    return render(request, 'posts/detail.html', context)
