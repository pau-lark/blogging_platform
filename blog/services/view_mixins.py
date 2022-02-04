from ..forms import PostCreationForm
from ..models import Post
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse_lazy


class PaginatorMixin:
    paginate_by = None

    def get_paginate_list(self, object_list):
        paginator = Paginator(object_list=object_list,
                              per_page=self.paginate_by)
        page = self.request.GET.get('page')
        try:
            object_list = paginator.page(page)
        except PageNotAnInteger:
            object_list = paginator.page(1)
        except EmptyPage:
            object_list = paginator.page(paginator.num_pages)
        return object_list


class PostEditMixin:
    form_class = PostCreationForm
    model = Post
    success_url = None
    template_name = 'posts/edit/create_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        self.success_url = reverse_lazy('blog:post_edit',
                                        kwargs={'post_id': self.object.id})
        return super().get_success_url()
