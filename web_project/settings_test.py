"""
Django settings for web_project project.

ENV_FILE_LOCATION - define the location of the .env configuration file
USE_CLOUD_SQL_AUTH_PROXY - True/False. Change the Mysql PORT to 5432 for using a proxy to GCP SQL
"""

from pathlib import Path
import os
import io
import environ
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env(DEBUG=(bool, False))
# env_file = os.path.join(BASE_DIR.parent, ".env")
env_file = os.path.join(BASE_DIR, ".env")
if os.environ.get('ENV_FILE_LOCATION', None):
    env_file = os.path.join(os.environ.get('ENV_FILE_LOCATION'), ".env")

if os.path.isfile(env_file):
    # Use a local secret file, if provided
    print('Load .env file')
    env.read_env(env_file)
else:
    placeholder = (
        f"SECRET_KEY=a\n"
        "GS_BUCKET_NAME=None\n"
        f"DATABASE_URL=sqlite://{os.path.join(BASE_DIR, 'db.sqlite3')}"
    )
    env.read_env(io.StringIO(placeholder))

# SECRET_KEY = 'django-insecure-rna9496%jo3u**+fetl60$4qyq9mx9xtcli+r$i0&5hb+s15^)'
SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# ALLOWED_HOSTS = ['localhost','127.0.0.1', 'ed1f29b.online-server.cloud']
ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    'hivebox.apps.HiveboxConfig',
    # 'rest_framework',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'asymmetric_jwt_auth',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'asymmetric_jwt_auth.middleware.JWTAuthMiddleware',
]

ROOT_URLCONF = 'web_project.urls'

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

WSGI_APPLICATION = 'web_project.wsgi.application'

# Database
DATABASES = {"default": env.db()}

if not DATABASES["default"]["HOST"] and '/' in DATABASES["default"]["NAME"]:
    s = DATABASES["default"]["NAME"]
    p = s.rfind('/',0, len(s))
    DATABASES["default"]["HOST"] = s[:p]
    DATABASES["default"]["NAME"] = s[p+1:]

# If the flag as been set, configure to use proxy
if os.getenv("USE_CLOUD_SQL_AUTH_PROXY", None):
    DATABASES["default"]["HOST"] = "127.0.0.1"
    DATABASES["default"]["PORT"] = 5432

print(DATABASES)

""" DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'vesko',
        'DATABASE': 'vesko',
        'USER': 'vesko',
        'PASSWORD': 'xxxxx',
        'HOST': 'localhost',
    }
} """


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/
# Define static storage via django-storages[google]
STATIC_URL = "/static/"

STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

#TEST_RUNNER = 'hivebox.test_runner.ManagedModelTestRunner'

#if 'test' in sys.argv:     
#    MIGRATION_MODULES = {         
#        'hivebox': 'hivebox.test_migrations',     
#    }
    #print('Echo from new settings')
#'hivebox.test_migrations'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True
        },
    }
}

HIVEBOX = {
    'AGGREGATE_THRESHOLD_HIGH': 1000,
    'AGGREGATE_THRESHOLD_LOW': 300,
}


REST_FRAMEWORK = {
    'COERCE_DECIMAL_TO_STRING': False,
    """ 'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ), """
    'DEFAULT_AUTHENTICATION_CLASSES': (
'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=14),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': False,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('JWT',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}