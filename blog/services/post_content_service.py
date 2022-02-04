from ..models import Post, Text
from account.services.decorators import query_debugger
from django.template.loader import render_to_string
from typing import Union


def get_text_preview_for_post(post: Post) -> Union[Text, None]:
    preview_content = post.contents.filter(content_type__model='text').first()
    if preview_content:
        return preview_content.content_object.text
    return None


@query_debugger
def get_post_content(post: Post) -> list:
    contents = []
    # prefetch ускоряет ~ с 0.09 до 0.08, возможно, принципиально на жирных постах
    for content in post.contents.all():
        content_object = content.content_object
        model_name = content.content_type.model
        content_template_response = render_to_string(f'posts/content/{model_name}.html',
                                                     {'content_object': content_object})
        contents.append(content_template_response)
    return contents
