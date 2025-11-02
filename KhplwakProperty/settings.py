# KhplwakProperty/settings.py
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# ───────── Security / Debug
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-insecure-key-only-for-local")
DEBUG = os.environ.get("DEBUG", "True").lower() == "true"   # True locally, set False on Render

# Render sets env RENDER=1. We’ll use it to toggle HTTPS there.
ON_RENDER = "RENDER" in os.environ

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "khplwakproperty.onrender.com",
    ".onrender.com",
]

# ───────── Apps
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "dealer",
    "widget_tweaks",
    "accounts",
    "django_extensions",  # optional; keep for runserver_plus etc.
]

# ───────── Middleware
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # required for static on Render
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "dealer.middleware.NoCacheForAuthenticatedPages",
]

ROOT_URLCONF = "KhplwakProperty.urls"

# ───────── Templates
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",
            BASE_DIR / "dealer" / "templates",
            BASE_DIR / "accounts" / "templates",
        ],
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

WSGI_APPLICATION = "KhplwakProperty.wsgi.application"

# ───────── Database (SQLite)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
# NOTE: On Render, SQLite resets unless you attach a disk. For tests/demos it’s fine.

# ───────── Password Validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ───────── I18N / TZ
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ───────── Static & Media
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Only include static dirs that actually exist (prevents W004 warnings)
STATICFILES_DIRS = []
for p in (BASE_DIR / "static", BASE_DIR / "dealer" / "static"):
    if p.exists():
        STATICFILES_DIRS.append(p)

# Django 5+ recommended storage API (works with WhiteNoise)
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    }
}

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ───────── Auth redirects
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "home"
LOGIN_URL = "login"

# ───────── CSRF trusted origins
CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    "https://khplwakproperty.onrender.com",
    "https://*.onrender.com",
    # Keep this so HTTPS dev (runserver_plus) works if you need it:
    "https://127.0.0.1:8000",
]

# ───────── HTTPS behavior
# Locally (DEBUG=True): NO HTTPS forcing → avoids ERR_SSL_PROTOCOL_ERROR if the browser cached HSTS.
# On Render (DEBUG=False or RENDER env): enable HTTPS & proxy header.
if not DEBUG or ON_RENDER:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
else:
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SECURE_PROXY_SSL_HEADER = None
