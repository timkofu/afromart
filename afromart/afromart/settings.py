import atexit
import json
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from socket import gethostbyname_ex, gethostname
from urllib.parse import urlparse

from django.contrib.messages import constants as messages

PROJECT_NAME = "afromart"  # Needs to be lowercase
DOMAIN_NAME = "afromart.trade"
PROJECT_DESCRIPTION = "The marketplace for Africa."


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "e59363d1f340c766ca9ad0dc3641a6d153689eaf8a9d303e03878455f5d4ee79"

DEBUG = not os.getenv("PRODUCTION")

ALLOWED_HOSTS = ["localhost"]
INTERNAL_IPS = ["127.0.0.1"]  # Makes settings.DEBUG available in templates.

CSRF_COOKIE_SECURE = True
SECURE_HSTS_PRELOAD = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SECURE_HSTS_SECONDS = 31536000
CSRF_COOKIE_SAMESITE = "Strict"
SESSION_COOKIE_SAMESITE = "Strict"
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_REFERRER_POLICY = "same-origin"
CSRF_TRUSTED_ORIGINS = (
    [f"https://{os.getenv(key='NGROK_DOMAIN')}"]
    if DEBUG
    else [f"https://{DOMAIN_NAME}"]
)


if not DEBUG:
    SECRET_KEY = os.getenv("SECRET_KEY")  # pyright: ignore[reportConstantRedefinition]
    ALLOWED_HOSTS = [DOMAIN_NAME]  # pyright: ignore[reportConstantRedefinition]
    USE_X_FORWARDED_HOST = True
    CSRF_COOKIE_DOMAIN = DOMAIN_NAME
    SESSION_COOKIE_DOMAIN = DOMAIN_NAME
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    # Dynamically allows any internal hostnames assigned by the PaaS
    try:
        ALLOWED_HOSTS.extend(
            [
                gethostname(),
            ]
            + list(set(gethostbyname_ex(gethostname())[2]))
        )
    except Exception:
        pass


INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.admin",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    # App
    "gate.apps.GateConfig",
    "trader.apps.TraderConfig",
    "payment.apps.PaymentConfig",
    "shipping.apps.ShippingConfig",
    "product.apps.ProductConfig",
    # 3rd Party
    "django_htmx",
]


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


ROOT_URLCONF = f"{PROJECT_NAME}.urls"


TEMPLATES = [  # pyright: ignore[reportUnknownVariableType]
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": (BASE_DIR / "templates",),
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                # Project context processors
                "afromart.context_processors.constants",
            ],
        },
    },
]


# Database
# dev_db:
#   postgres=# create user afromart with createdb password 'afromart';
#   postgres=# create database afromart owner afromart;
database_credentials = urlparse(url=os.getenv("DATABASE_URL"))
DATABASES = {  # pyright: ignore[reportUnknownVariableType]
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "PORT": database_credentials.port,
        "NAME": database_credentials.path[1:],
        "USER": database_credentials.username,
        "HOST": database_credentials.hostname,
        "PASSWORD": database_credentials.password,
        "CONN_MAX_AGE": 30,
        "CONN_HEALTH_CHECKS": True,
        "DISABLE_SERVER_SIDE_CURSORS": True,
        "OPTIONS": {
            "keepalives": 1,
            "connect_timeout": 10,
            "keepalives_idle": 20,
            "keepalives_count": 6,
            "keepalives_interval": 5,
            "application_name": PROJECT_NAME,
        },
    }
}
if not DEBUG:
    DATABASES["default"]["OPTIONS"].update(  # pyright: ignore[reportUnknownMemberType]
        {
            "sslmode": "require",
            "channel_binding": "require",
        }
    )


CACHES = {  # pyright: ignore[reportUnknownVariableType]
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": os.getenv(key="CACHE_URL"),
        "KEY_PREFIX": f"{PROJECT_NAME}_",
        "OPTIONS": {
            "socket_timeout": 5,
            "max_connections": 10,
            "socket_keepalive": True,
            "retry_on_timeout": True,
            "health_check_interval": 30,
            "socket_connect_timeout": 5,
        },
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"


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


LOGIN_URL = "/gate/signin/"


USE_TZ = True
USE_I18N = False
TIME_ZONE = "UTC"
LANGUAGE_CODE = "en"
LANGUAGES = [("en", "English")]


STATIC_URL = "static/"
MEDIA_ROOT = BASE_DIR / "media"
STATIC_ROOT = BASE_DIR / "static"
STATICFILES_DIRS = (BASE_DIR / "static_global",)


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Email
EMAIL = f"{PROJECT_NAME}@{DOMAIN_NAME}"
EMAIL_CREDENTIALS = json.loads(os.getenv("EMAIL_CREDENTIALS", '{"": ""}'))
EMAIL_HOST = EMAIL_CREDENTIALS.get("host")
EMAIL_PORT = 587
EMAIL_HOST_USER = EMAIL_CREDENTIALS.get("username")
EMAIL_HOST_PASSWORD = EMAIL_CREDENTIALS.get("password")
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = f"{PROJECT_NAME.capitalize()} <{EMAIL}>"
SERVER_EMAIL = EMAIL
ADMINS = [
    ("Timothy", "tim.makobu@gmail.com"),
]
EMAIL_SUBJECT_PREFIX = f"[{PROJECT_NAME.capitalize()}]: "
EMAIL_BACKEND = (
    "django.core.mail.backends.smtp.EmailBackend"
    if not DEBUG
    else "django.core.mail.backends.console.EmailBackend"
)


# Logging
# Define PrefixFilter before LOGGING
class PrefixFilter(logging.Filter):
    def filter(self, record: logging.LogRecord):
        record.msg = f"[{PROJECT_NAME.capitalize()}] {record.msg}"
        return True


LOGGING = {  # pyright: ignore[reportUnknownVariableType]
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "production": {
            "format": "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "development": {
            "format": "[%(asctime)s] [%(process)d] [%(levelname)s] [%(module)s:%(lineno)d] %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "filters": {
        "prefix_filter": {"()": PrefixFilter},
        "require_debug_false": {"()": "django.utils.log.RequireDebugFalse"},
    },
    "handlers": {
        "console": {
            "level": "DEBUG" if DEBUG else "INFO",
            "class": "logging.StreamHandler",
            "formatter": "development" if DEBUG else "production",
            "filters": ["prefix_filter"],
        },
        "mail_admins": {
            "level": "ERROR",
            "class": "django.utils.log.AdminEmailHandler",
            "filters": ["require_debug_false", "prefix_filter"],
            "include_html": True,
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "mail_admins"],
            "level": "INFO",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["console", "mail_admins"],
            "level": "ERROR",
            "propagate": False,
        },
        "django.security": {
            "handlers": ["console", "mail_admins"],
            "level": "WARNING",
            "propagate": False,
        },
        f"{PROJECT_NAME}": {
            "handlers": ["console"],
            "level": "DEBUG" if DEBUG else "INFO",
            "propagate": False,
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
}

LOGGER = logging.getLogger(name=PROJECT_NAME)


# Shared ThreadPool
THREAD_POOL = ThreadPoolExecutor(max_workers=2, thread_name_prefix=f"{PROJECT_NAME}_")
atexit.register(THREAD_POOL.shutdown, wait=True)


# Use Bootstrap colors for django.contrib.messages
MESSAGE_TAGS = {
    messages.DEBUG: "secondary",
    messages.INFO: "info",
    messages.SUCCESS: "success",
    messages.WARNING: "warning",
    messages.ERROR: "danger",
}
