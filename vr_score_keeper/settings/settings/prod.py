import os
import dj_database_url
from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
# Reads the DJANGO_DEBUG environment variable, defaulting to False.
DEBUG = os.environ.get("DJANGO_DEBUG", "False").lower() in ("true", "1", "t")

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY", "")

# Read allowed hosts from the environment. This should be a comma-separated
# list of your domain(s), e.g., "your-domain.com,www.your-domain.com"
allowed_hosts_str = os.environ.get("DJANGO_ALLOWED_HOSTS")
if allowed_hosts_str:
    ALLOWED_HOSTS = [host.strip() for host in allowed_hosts_str.split(",")]
else:
    # It's safer to have an empty list than ["*"] if the variable isn't set.
    ALLOWED_HOSTS = []

# Read CSRF trusted origins from the environment. This should be a comma-separated
# list of your full HTTPS domain(s), e.g., "https://your-domain.com,https://www.your-domain.com"
csrf_trusted_origins_str = os.environ.get("DJANGO_CSRF_TRUSTED_ORIGINS")
if csrf_trusted_origins_str:
    CSRF_TRUSTED_ORIGINS = [
        origin.strip() for origin in csrf_trusted_origins_str.split(",")
    ]
else:
    CSRF_TRUSTED_ORIGINS = []

# Secure cookies
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Security headers
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_SSL_REDIRECT = True

# Set HSTS headers (adjust max_age as needed)
# Start with a small value for testing, e.g., 3600, before committing to a long duration.
# SECURE_HSTS_SECONDS = int(os.environ.get('DJANGO_SECURE_HSTS_SECONDS', 0))
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True

# Required for Django to trust the 'https' scheme from the reverse proxy
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Database configuration using dj-database-url.
# This reads the DATABASE_URL environment variable.
# Example: postgres://user:password@host:port/dbname
DATABASES = {
    # Set ssl_require=True if your external database requires SSL.
    "default": dj_database_url.config(conn_max_age=600, ssl_require=False)
}

# Static files storage with whitenoise for production.
# http://whitenoise.evans.io/en/stable/django.html#add-compression-and-caching-support
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
