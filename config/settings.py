from pathlib import Path
import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/


env = environ.Env()
environ.Env.read_env()


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'account.apps.AccountConfig',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'crispy_forms',
    'sorl.thumbnail',
    'embed_video',

    'blog.apps.BlogConfig'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR.joinpath('templates')
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # context processor для категорий
                'blog.context_processors.category',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST'),
        'PORT': env('DB_PORT'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# переопределяем ссылку на User model
AUTH_USER_MODEL = 'account.CustomUser'


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'Europe/Kirov'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = 'static/'

STATICFILES_DIRS = [
    BASE_DIR.joinpath('static')
]

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR.joinpath('media')

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Login, logout, redirect urls
LOGIN_REDIRECT_URL = 'blog:article_list'
LOGIN_URL = 'login'
LOGOUT_URL = 'logout'


CRISPY_TEMPLATE_PACK = 'bootstrap4'


# simulator smtp
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


# redis settings
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0


USER_RATING_BY_ACTION = {
    'init': 0,
    'add_subscriber': 10,
    'delete_subscriber': -10,
    'create_article': 25,
    'delete_article': -25
}

ARTICLE_RATING_BY_ACTION = {
    'init': 0,
    'view': 1,
    'like': 3,
    'unlike': -3,
    'comment': 5
}

ARTICLE_FILTER_LIST = {
    'all': 'Все',
    'subscriptions': 'Подписки'
}
ARTICLE_ORDER_LIST = {
    'rating': 'По рейтингу',
    'date': 'Последние'
}
USER_ARTICLE_STATUS_FILTER_LIST = {
    'publish': 'Публикации',
    'draft': 'Черновики'
}
USER_FILTER_LIST = {
    'all': 'Все',
    'subscriptions': 'Подписки',
    'subscribers': 'Подписчики'
}
USER_ORDER_LIST = {
    'rating': 'По рейтингу',
    'article_count': 'По количеству постов'
}

ARTICLE_CONTENT_TYPES = {
    'text': 'Текст',
    'image': 'Изображение',
    'video': 'Видео'
}

ALPHABET = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo', 'ж': 'zh',
    'з': 'z', 'и': 'i', 'й': 'j', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o',
    'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'ts',
    'ч': 'ch', 'ш': 'sh', 'щ': 'shch', 'ы': 'i', 'э': 'e', 'ю': 'yu', 'я': 'ya'
}


LOG_DIR = BASE_DIR.joinpath('logs')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'console_formatter': {
            'format': '{levelname} {module} {message}',
            'style': '{',
        },
        'file_formatter': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'console_formatter',
        },
        'account_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': f'{LOG_DIR}/account.log',
            'formatter': 'file_formatter',
        },
        'blog_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': f'{LOG_DIR}/blog.log',
            'formatter': 'file_formatter',
        },
    },
    'loggers': {
        'account_logger': {
            'handlers': ['console', 'account_file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'blog_logger': {
            'handlers': ['console', 'blog_file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
