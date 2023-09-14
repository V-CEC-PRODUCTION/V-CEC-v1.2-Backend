"""
Django settings for vcec_bk project.

Generated by 'django-admin startproject' using Django 4.2.4.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
import os 
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-m1tzb)nx&22@lnwx2%v@+pgji&6aj%egiggjut*z^tua&8nxs_'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'users',
    'notices',
    'homepage_images',
    'staff_info',
    'highlights_cec',
    'gallery_cec',
    'forum_events',
    'forum_announcements',
    'timetables'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'vcec_bk.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'vcec_bk.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',  # Database engine
        'NAME': 'vcec',              # Database name
        'USER': 'vcec_1',              # Database user
        'PASSWORD': '@proddec2023',      # Database password
        'HOST': 'vcec.postgres.database.azure.com',                       # Database host (default is 'localhost')
        'PORT': '5432',                            # Database port (default is '5432')
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'rediss://vcec.redis.cache.windows.net:6380',  # Replace with your Redis server address and database number
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'PASSWORD': 'mR1pEV4aiMNSGJeCI9QIhifJxRo2QcQy3AzCaHBT0lc=',
            'SSL' :True,
        
        }
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"


# Celery settings
CELERY_BROKER_URL = 'rediss://:mR1pEV4aiMNSGJeCI9QIhifJxRo2QcQy3AzCaHBT0lc=@vcec.redis.cache.windows.net:6380'+ '?ssl_cert_reqs=none'
CELERY_RESULT_BACKEND = 'rediss://:mR1pEV4aiMNSGJeCI9QIhifJxRo2QcQy3AzCaHBT0lc=@vcec.redis.cache.windows.net:6380'+ '?ssl_cert_reqs=none'
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True 

CELERY_BEAT_SCHEDULE_FILENAME = 'celerybeat-schedule'  


CELERY_BEAT_SCHEDULE = {
    'scrape-every-15-minutes': {
        'task': 'notices.tasks.ktu_webs_announce_task',
        'schedule': 900,  # 15 minutes in seconds
    },
}

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp-relay.brevo.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'proddecapp@gmail.com'
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASSWORD')


ACCESS_TOKEN_EXPIRATION = 120 # Adjust as needed
REFRESH_TOKEN_EXPIRATION = 483840 # Adjust as needed


MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
