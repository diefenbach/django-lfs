"""Settings for django-lfs's tests: LFS with the default theme and no optional add-ons, SQLite in memory.

Tests that need an optional add-on (lfs_paypal, lfs_bulk_prices, ...) skip themselves when it is not installed.
"""

from pathlib import Path

from lfs.settings import LFS_APPS

BASE_DIR = Path(__file__).resolve().parent

DEBUG = False
SECRET_KEY = "django-lfs-tests-only"
ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1"]

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

INSTALLED_APPS = ["lfs_theme", *LFS_APPS]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
ROOT_URLCONF = "tests.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "lfs.core.context_processors.main",
            ],
        },
    },
]

AUTHENTICATION_BACKENDS = ["lfs.customer.auth.EmailBackend", "django.contrib.auth.backends.ModelBackend"]
LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/manage/"

LANGUAGE_CODE = "en"
TIME_ZONE = "Europe/Berlin"
USE_I18N = True
USE_TZ = True
SITE_ID = 1
SESSION_SERIALIZER = "lfs.core.pickle_serializer.PickleSerializer"

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "static"
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "compressor.finders.CompressorFinder",
]
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"
COMPRESS_ENABLED = False

CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"
