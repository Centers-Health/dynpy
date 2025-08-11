import os

import django

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Choose database for settings
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}

INSTALLED_APPS = (
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.sites",
    "django.contrib.humanize",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.admin.apps.SimpleAdminConfig",
    "django.contrib.staticfiles",
    "crispy_forms",
    "dynpy",
    "dynpy_gfl",
    "dynpy_actions",
    "dynpy_forms",
    "hx_requests",
    "tests",
)
ROOT_URLCONF = "tests.urls"

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

MIDDLEWARE = (
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
)

TEMPLATES = (
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(BASE_DIR, "templates"),
            django.__path__[0] + "/forms/templates",
        ],
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
)

STATIC_URL: str = "/static/"  # Url to find the static files at

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "dynpy_gfl/static")
]  # Where our static files live in the codebase

SECRET_KEY = "django-insecure-)9hmvjz_nxa=r2a3dv@upzlvbcm6fu1yej28sn6%3"
