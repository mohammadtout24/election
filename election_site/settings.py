import os
from pathlib import Path
import dj_database_url
from django.core.exceptions import ImproperlyConfigured
import sys # ADDED: Required for checking management commands

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# =========================================================================
# 1. SECURITY AND ENVIRONMENT CONFIGURATION
# =========================================================================

# Reading DEBUG flag first. Default to False for production if not set.
# Use an environment variable like DJANGO_DEBUG=True for development/staging environments.
DEBUG = os.environ.get('DJANGO_DEBUG', 'False').lower() in ('true', '1')

# Reading SECRET_KEY from environment variable
SECRET_KEY = os.environ.get('SECRET_KEY')

# Detect if we are running a management command during the build phase (like collectstatic)
# This allows the settings file to load even if the SECRET_KEY is not available in the build environment.
IS_BUILD_COMMAND = any(cmd in sys.argv for cmd in ['collectstatic', 'makemigrations'])

if not SECRET_KEY:
    if DEBUG or IS_BUILD_COMMAND:
        # FIX: Use a dummy key for local development or for safe build commands
        print("WARNING: Using insecure default SECRET_KEY for local development or build command.")
        # NOTE: Generate a real key if you share this code or move to staging!
        SECRET_KEY = 'insecure-default-key-for-local-dev-only' 
    else:
        # Raise an error if the SECRET_KEY is not set in production (DEBUG=False)
        # This will fail the application if the webserver starts without a key, ensuring security.
        raise ImproperlyConfigured("The SECRET_KEY environment variable must be set when DEBUG is False.")


# This is the FIX for the DisallowedHost error.
# We read the primary host from a Render environment variable or fallback to an
# environment variable named 'ALLOWED_HOSTS' if available.
# We also ensure that any hosts specified in the RENDER_EXTERNAL_HOSTNAME are accepted.
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# Fallback for generic ALLOWED_HOSTS variable
if os.environ.get('ALLOWED_HOSTS'):
    # Extend list, splitting comma-separated values from the environment variable
    ALLOWED_HOSTS.extend(
        host.strip()
        for host in os.environ.get('ALLOWED_HOSTS').split(',')
        if host.strip()
    )


# Recommended setting for running behind a proxy like Render
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


# =========================================================================
# 2. APPLICATION DEFINITION (Add your project apps here)
# =========================================================================

INSTALLED_APPS = [
    # Django default apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    # WhiteNoise is now configured to handle static files in production.
    'django.contrib.staticfiles',

    # Third-party apps from requirements.txt
    'ckeditor',
    'django_js_asset', # required by django-ckeditor

    # Your project apps (Example: 'polls', 'elections')
    # ...
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # WhiteNoise Middleware must be placed directly after SecurityMiddleware
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'election_site.urls' # Assuming 'election_site' is your project name

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

WSGI_APPLICATION = 'election_site.wsgi.application' # Assuming 'election_site' is your project name


# =========================================================================
# 3. DATABASE CONFIGURATION (Using dj-database-url and psycopg2-binary)
# =========================================================================

# The DATABASE_URL is automatically provided by Render for PostgreSQL databases.
# dj-database-url handles the parsing and configuration for us.
# The default SQLite config is used if DATABASE_URL is not found (e.g., in local dev).
DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///' + os.path.join(BASE_DIR, 'db.sqlite3'),
        conn_max_age=600,
        conn_health_checks=True, # FIXED: Changed 'conn_health_check' to 'conn_health_checks'
    )
}


# =========================================================================
# 4. STATIC FILES CONFIGURATION (Using WhiteNoise)
# =========================================================================

# The application failed because it was trying to serve static files in production,
# which requires WhiteNoise (the package you selected) to be set up.

STATIC_URL = 'static/'
# This tells Django where to collect all static files for production
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Extra places for collectstatic to find static files.
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Tell WhiteNoise to use the ManifestStaticFilesStorage engine
# This is crucial for performance and caching static assets.
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# =========================================================================
# 5. OTHER DEFAULT SETTINGS
# =========================================================================

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    # ... default password validators ...
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# CKEDITOR CONFIGURATION
CKEDITOR_UPLOAD_PATH = 'uploads/'

# Optional: Configuration for CKEditor
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
        'height': 300,
        'width': '100%',
    },
}
