from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic.base import View


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
