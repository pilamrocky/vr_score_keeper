import os
from .base import *

DEBUG = False

# Production Database using PostgreSQL
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.environ.get("POSTGRES_DB"),
        "USER": os.environ.get("POSTGRES_USER"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD"),
        "HOST": os.environ.get(
            "POSTGRES_HOST", "db"
        ),  # Default to 'db' if environment variable is not set.
        "PORT": os.environ.get(
            "POSTGRES_PORT", "5432"
        ),  # Default to '5432' if environment variable is not set
    }
}
