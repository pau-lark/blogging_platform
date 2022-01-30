from django.db import connection, reset_queries
from django.http import HttpResponseBadRequest
import functools
import time


def query_debugger(func):
    @functools.wraps(func)
    def inner_func(*args, **kwargs):
        reset_queries()

        start_queries = len(connection.queries)

        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()

        end_queries = len(connection.queries)

        print(f"Function : {func.__name__}")
        print(f"Number of Queries : {end_queries - start_queries}")
        print(f"Finished in : {(end - start):.2f}s")
        return result
    return inner_func


def ajax_required(func):
    def wrap(request, *args, **kwargs):
        if request.is_ajax():
            return func(request, *args, **kwargs)
        return HttpResponseBadRequest()
    wrap.__doc__ = func.__doc__
    wrap.__name__ = func.__name__
    return wrap
