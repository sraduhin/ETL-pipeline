# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases
import os

from config.components.app import DEBUG

HOST = os.environ.get("POSTGRES_HOST", "127.0.0.1") if DEBUG else "db"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB"),
        "USER": os.environ.get("POSTGRES_USER"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD"),
        "HOST": HOST,
        "PORT": os.environ.get("POSTGRES_PORT", 5432),
        "OPTIONS": {"options": "-c search_path=public,content"},
    }
}
