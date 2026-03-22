# pylint: disable=missing-module-docstring
import logging
import os

import ldap
import sentry_sdk
from django.contrib.messages import constants as messages
from django_auth_ldap.config import LDAPSearch

# Load environment variables from .env file
from dotenv import find_dotenv, load_dotenv
from sentry_sdk.integrations.django import DjangoIntegration

load_dotenv(find_dotenv())


# Current project version
PROJECT_VERSION = "v1.1"
PROJECT_ENV = os.environ["DJANGO_ENVIRONMENT"]

sentry_sdk.init(
    dsn=os.environ["SENTRY_DSN"],
    integrations=[DjangoIntegration()],
    environment=PROJECT_ENV,
    release=PROJECT_VERSION,
    server_name=os.getenv("SENTRY_SERVER_NAME", f"{PROJECT_ENV}-server"),
)

DEBUG = bool(PROJECT_ENV != "production")
DEBUG_PROPAGATE_EXCEPTIONS = bool(PROJECT_ENV != "production")

ALLOWED_HOSTS = ["*"]

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")

INSTALLED_APPS = [
    "dal",
    "dal_select2",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "compressor",
    "rolepermissions",
    "localflavor",
    "crispy_forms",
    "django_filters",
    "mathfilters",
    "dbbackup",
    "accounts",
    "escribadbquery",
    "relatorios",
    "pages",
    "depositos",
    "guiches",
    "caixa",
    "despesas",
    "clientes",
    "api_cartoes",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",  # session timeout
    "django_session_timeout.middleware.SessionTimeoutMiddleware",  # session timeout
]

ROOT_URLCONF = "contabil.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "contabil.wsgi.application"

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# ==== DATABASE CONFIGURATIONS ==== #
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

SQLITE_DB = {
    "ENGINE": "django.db.backends.sqlite3",
    "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
}
MYSQL_DB = {
    "ENGINE": "django.db.backends.mysql",
    "NAME": os.getenv("MYSQL_DATABASE"),
    "USER": os.getenv("MYSQL_USER"),
    "PASSWORD": os.getenv("MYSQL_PASSWORD"),
    "HOST": os.getenv("MYSQL_HOST"),
    "PORT": os.getenv("MYSQL_PORT"),
}

DATABASES = {"default": SQLITE_DB if not os.getenv("MYSQL_DATABASE") else MYSQL_DB}


# ==== PASSWORD VALIDATION ==== #
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# ==== INTERNATIONALIZATION ==== #
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_L10N = True
USE_TZ = True
THOUSAND_SEPARATOR = "."


# ==== SESSION EXPIRATION SETTINGS ==== #
SESSION_EXPIRE_SECONDS = 60 * 60 * 12  # 12 horas
SESSION_EXPIRE_AFTER_LAST_ACTIVITY = True


# ==== STATIC AND MEDIA FILE SETTINGS ==== #
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "assets"),
]
STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "compressor.finders.CompressorFinder",
)

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")


# ==== CRISPY TEMPLATE PACKAGE SETTINGS ==== #
CRISPY_TEMPLATE_PACK = "bootstrap4"
CRISPY_FAIL_SILENTLY = False  # not DEBUG


# ==== CUSTOM ACCOUNTS MODEL ==== #
AUTH_USER_MODEL = "accounts.ProjectUser"


# ==== LOGIN / LOGOUT REDIRECT ==== #
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "home"


# ==== ROLEPERMISSIONS PACKAGE SETTINGS ==== #
ROLEPERMISSIONS_MODULE = "contabil.roles"
# ROLEPERMISSIONS_REDIRECT_TO_LOGIN = True


# ==== SETTINGS TO MAP MESSAGES TO BOOTSTRAP CLASSES ==== #
MESSAGE_TAGS = {
    messages.DEBUG: "alert-info",
    messages.INFO: "alert-info",
    messages.SUCCESS: "alert-success",
    messages.WARNING: "alert-warning",
    messages.ERROR: "alert-danger",
}


# DBBACKUP SETTINGS
DBBACKUP_STORAGE = "django.core.files.storage.FileSystemStorage"
DBBACKUP_STORAGE_OPTIONS = {"location": "/var/backups"}


# ==== DJANGO-AUTH-LDAP CONFIGURATION ==== #
AUTH_LDAP_SERVER_URI = os.environ["AUTH_LDAP_SERVER_URI"]

AUTH_LDAP_BIND_DN = os.environ["AUTH_LDAP_BIND_DN"]
AUTH_LDAP_BIND_PASSWORD = os.environ["AUTH_LDAP_BIND_PASSWORD"]
AUTH_LDAP_USER_SEARCH = LDAPSearch(
    os.environ["AUTH_LDAP_USER_SEARCH_OU"],
    ldap.SCOPE_SUBTREE,  # pylint: disable=no-member
    "(sAMAccountName=%(user)s)",
)

AUTH_LDAP_USER_ATTR_MAP = {
    "first_name": "givenName",
    "last_name": "sn",
    "email": "mail",
}

AUTH_LDAP_ALWAYS_UPDATE_USER = True

AUTH_LDAP_CACHE_GROUPS = True
AUTH_LDAP_GROUP_CACHE_TIMEOUT = 3600

AUTHENTICATION_BACKENDS = (
    "django_auth_ldap.backend.LDAPBackend",
    "django.contrib.auth.backends.ModelBackend",
)


# ==== LOGGING CONFIGURATIONS TO DEBUG THE PROJECT ==== #
logger = logging.getLogger("django_auth_ldap")
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

# send logging to the console #
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "filters": {
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        }
    },
    "handlers": {
        "console": {
            "level": os.getenv("DJANGO_LOG_LEVEL", "INFO").upper(),
            # "filters": ["require_debug_true"],
            "class": "logging.StreamHandler",
            "formatter": "simple",
        }
    },
    "loggers": {
        "django": {
            "level": "DEBUG",
            "handlers": ["console"],
            "propagate": True,
        },
        "afinco": {
            "handlers": ["console"],
            "propagate": True,
            "level": os.getenv("AFINCO_LOG_LEVEL", "INFO").upper(),
        },
    },
}
