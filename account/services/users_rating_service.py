from django.conf import settings
import redis


REDIS = redis.StrictRedis(host=settings.REDIS_HOST,
                          port=settings.REDIS_PORT,
                          db=settings.REDIS_DB)


class Rating:
    rating_by_action = {
        'view': 1,
        'like': 3,
        'comment': 5,
        'subscriber': 10,
        'create_post': 25
    }

    def get_user_rating(self, user_id):
        # zscore
        pass

    def get_all_user_rating(self):
        # zrange
        pass

    def add_user_rating(self, user_id, action):
        # zincrby
        pass

    def calculate_total_user_rating(self, user_id):
        pass

    def clear_user_rating(self, user_id):
        pass
