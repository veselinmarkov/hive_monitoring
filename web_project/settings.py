"""
Django settings for web_project project.

ENV_FILE_LOCATION - define the location of the .env configuration file
GOOGLE_CLOUD_PROJECT - project name in GCP. Set if the project is depolyed to GCP
USE_CLOUD_SQL_AUTH_PROXY - True/False. Change the Mysql PORT to 5432 for using a proxy to GCP SQL
SETTINGS_NAME - (default:'djangp_settings') name of the configuration secret in GCP 
RUN_TEST - Setup a SQLite db for testing
DEVELOP - True/False set the DEBUG flag in the Django project (must be False for production)
"""

from pathlib import Path
import os
import io
import environ
from datetime import timedelta
import google.auth
from google.cloud import secretmanager

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env(DEBUG=(bool, False))
ENV_NAME = ".env"
env_file = os.path.join(BASE_DIR, ENV_NAME)
file_location = os.environ.get('ENV_FILE_LOCATION', None)
if file_location:
    print('ENV_FILE_LOCATION =%s' % (os.environ.get('ENV_FILE_LOCATION')))
    if file_location[-len(ENV_NAME):] ==ENV_NAME:
        # the file name (.env) appear at the end of the file_location
        env_file = file_location
    else:
        env_file = os.path.join(os.environ.get('ENV_FILE_LOCATION'), ".env")

# Attempt to load the Project ID into the environment, safely failing on error.
try:
    _, os.environ["GOOGLE_CLOUD_PROJECT"] = google.auth.default()
except google.auth.exceptions.DefaultCredentialsError:
    pass

project_id = None
if os.path.isfile(env_file):
    # Use a local secret file, if provided
    print('Load .env file')
    env.read_env(env_file)
elif os.environ.get("RUN_TEST", None):
    placeholder = (
        f"SECRET_KEY=a\n"
        "GS_BUCKET_NAME=None\n"
        f"DATABASE_URL=sqlite://{os.path.join(BASE_DIR, 'db.sqlite3')}"
    )
    env.read_env(io.StringIO(placeholder))
elif os.environ.get("GOOGLE_CLOUD_PROJECT", None):
    # Pull secrets from Secret Manager
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")

    client = secretmanager.SecretManagerServiceClient()
    settings_name = os.environ.get("SETTINGS_NAME", "django_settings")
    name = f"projects/{project_id}/secrets/{settings_name}/versions/latest"
    payload = client.access_secret_version(name=name).payload.data.decode("UTF-8")

    env.read_env(io.StringIO(payload))
else:
    raise Exception("No local .env or GOOGLE_CLOUD_PROJECT detected. No secrets found.")


# SECRET_KEY = 'django-insecure-rna9496%jo3u**+fetl60$4qyq9mx9xtcli+r$i0&5hb+s15^)'
SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = (os.getenv("DEVELOP", False))

# ALLOWED_HOSTS = ['localhost','127.0.0.1', 'ed1f29b.online-server.cloud']
ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    'hivebox.apps.HiveboxConfig',
    'rest_framework',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 'web_project',
    # 'storages',
    'asymmetric_jwt_auth',
]

if project_id:
    INSTALLED_APPS.append('web_project')
    INSTALLED_APPS.append('storages')

# print(INSTALLED_APPS)

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

""" if not DATABASES['default']['HOST'] :
    DATABASES['default']['HOST'] = 'localhost' """

print('Database name=%s, Database host=%s, Database engine=%s' % (DATABASES["default"]["NAME"], 
    DATABASES["default"]["HOST"], DATABASES["default"]["ENGINE"]))

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

if project_id:
    GS_BUCKET_NAME = env("GS_BUCKET_NAME")
    DEFAULT_FILE_STORAGE = "storages.backends.gcloud.GoogleCloudStorage"
    STATICFILES_STORAGE = "storages.backends.gcloud.GoogleCloudStorage"
    GS_DEFAULT_ACL = "publicRead"

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

ASYMMETRIC_JWT_AUTH = {
    'NONCE_BACKEND' : 'asymmetric_jwt_auth.nonce.null.NullNonceBackend',
    'TIMESTAMP_TOLERANCE' : 120
}