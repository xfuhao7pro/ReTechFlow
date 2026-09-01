import os
from datetime import timedelta
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from corsheaders.defaults import default_headers
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

from backend.project_config import PROJECT_CONFIG


def env_bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


def env_list(name: str, default: str = "") -> list[str]:
    return [item.strip() for item in os.getenv(name, default).split(",") if item.strip()]


SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "django-insecure-dev-only-change-me")
DEBUG = env_bool("DJANGO_DEBUG", True)
ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1" if DEBUG else "")

if not DEBUG and SECRET_KEY == "django-insecure-dev-only-change-me":
    raise ImproperlyConfigured("DJANGO_SECRET_KEY must be configured when DJANGO_DEBUG=False")
if not DEBUG and not ALLOWED_HOSTS:
    raise ImproperlyConfigured("DJANGO_ALLOWED_HOSTS must be configured when DJANGO_DEBUG=False")

INSTALLED_APPS = [
    "daphne",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "channels",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "apps.users",
    "apps.goods",
    "apps.chats",
    "apps.orders",
    "rest_framework",
    "rest_framework_simplejwt",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "backend.urls"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]
WSGI_APPLICATION = "backend.wsgi.application"
ASGI_APPLICATION = "backend.asgi.application"

# Keep database credentials local in mysql.cnf. This preserves the existing schema contract.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "OPTIONS": {
            "read_default_file": str(BASE_DIR / "mysql.cnf"),
        },
    },
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "zh-hans"
TIME_ZONE = "Asia/Shanghai"
USE_I18N = True
USE_TZ = False

CORS_ALLOW_ALL_ORIGINS = env_bool("CORS_ALLOW_ALL_ORIGINS", DEBUG)
CORS_ALLOWED_ORIGINS = env_list("CORS_ALLOWED_ORIGINS")
CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS")
CORS_ALLOW_HEADERS = (*default_headers, "x-guest-token")

AUTH_USER_MODEL = "users.PlatformUser"
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_THROTTLE_CLASSES": (
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ),
    "DEFAULT_THROTTLE_RATES": {
        "anon": os.getenv("DRF_ANON_THROTTLE_RATE", "60/minute"),
        "user": os.getenv("DRF_USER_THROTTLE_RATE", "300/minute"),
    },
    "EXCEPTION_HANDLER": "backend.exceptions.api_exception_handler",
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=int(os.getenv("JWT_ACCESS_MINUTES", "30"))),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=int(os.getenv("JWT_REFRESH_DAYS", "7"))),
    "AUTH_HEADER_TYPES": ("Bearer",),
}

ZHIPUAI_API_KEY = PROJECT_CONFIG["zhipuai_api_key"]
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = PROJECT_CONFIG["email"]["host"]
EMAIL_PORT = PROJECT_CONFIG["email"]["port"]
EMAIL_USE_SSL = PROJECT_CONFIG["email"]["use_ssl"]
EMAIL_HOST_USER = PROJECT_CONFIG["email"]["user"]
EMAIL_HOST_PASSWORD = PROJECT_CONFIG["email"]["password"]
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
EMAIL_TIMEOUT = int(os.getenv("EMAIL_TIMEOUT", "5"))

REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/1")
CACHE_BACKEND = os.getenv("CACHE_BACKEND", "memory" if DEBUG else "redis")
if CACHE_BACKEND == "memory":
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "retech-flow-local-cache",
        },
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": REDIS_URL,
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            },
        },
    }

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

if os.getenv("CHANNEL_LAYER_BACKEND", "memory" if DEBUG else "redis") == "memory":
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels.layers.InMemoryChannelLayer",
        },
    }
else:
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": [REDIS_URL],
            },
        },
    }

SECURE_SSL_REDIRECT = env_bool("DJANGO_SECURE_SSL_REDIRECT", not DEBUG)
SESSION_COOKIE_SECURE = env_bool("DJANGO_SESSION_COOKIE_SECURE", not DEBUG)
CSRF_COOKIE_SECURE = env_bool("DJANGO_CSRF_COOKIE_SECURE", not DEBUG)
SECURE_HSTS_SECONDS = int(os.getenv("DJANGO_SECURE_HSTS_SECONDS", "0" if DEBUG else "31536000"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool("DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS", not DEBUG)
SECURE_HSTS_PRELOAD = env_bool("DJANGO_SECURE_HSTS_PRELOAD", not DEBUG)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "{asctime} {levelname} {name} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
    },
}

KUAIDI100_CUSTOMER = os.getenv("KUAIDI100_CUSTOMER", "")
KUAIDI100_KEY = os.getenv("KUAIDI100_KEY", "")
ENABLE_MOCK_RECHARGE = env_bool("ENABLE_MOCK_RECHARGE", DEBUG)
