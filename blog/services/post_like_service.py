from ..models import Post
from .post_rating_service import PostsRating
from .posts_range_service import get_post_object


RATING = PostsRating()


def like_post(user, post_id: int, action: str) -> bool:
    try:
        post = get_post_object(int(post_id))
        if action == 'like':
            post.users_like.add(user)
            RATING.incr_or_decr_rating_by_id(action='like',
                                             object_id=post_id)
        else:
            post.users_like.remove(user)
            RATING.incr_or_decr_rating_by_id(action='unlike',
                                             object_id=post_id)
        return True
    except Post.DoesNotExist:
        # TODO: в лог
        return False
