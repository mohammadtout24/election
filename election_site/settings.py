import os
from pathlib import Path
import dj_database_url
from django.core.exceptions import ImproperlyConfigured
import sys

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# =========================================================================
# 1. SECURITY AND ENVIRONMENT CONFIGURATION
# =========================================================================

# Reading DEBUG flag first. Default to False for production if not set.
DEBUG = os.environ.get('DJANGO_DEBUG', 'True').lower() in ('true', '1') # Set default to True for local ease

# Reading SECRET_KEY from environment variable (or using the local default)
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-er0jayjfdjcdpy&jfkfjq4w@^^f4-_9%wyx6lw&7(cqf)^wr&r') 

# Detect if we are running a management command during the build phase (like collectstatic)
IS_BUILD_COMMAND = any(cmd in sys.argv for cmd in ['collectstatic', 'makemigrations'])

# Ensure SECRET_KEY is secure if running in production (DEBUG=False)
if not DEBUG and not os.environ.get('SECRET_KEY'):
    # This prevents running the web server on a public host with an insecure key
    raise ImproperlyConfigured("The SECRET_KEY environment variable must be set when DEBUG is False.")


ALLOWED_HOSTS = ['127.0.0.1', 'election-btyx.onrender.com']

# Safely extend ALLOWED_HOSTS for Render
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# Recommended setting for running behind a proxy like Render
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


# =========================================================================
# 2. APPLICATION DEFINITION
# =========================================================================

INSTALLED_APPS = [
    # Django default apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'ckeditor',
    'django_js_asset', # required by django-ckeditor

    # Your project apps
    'candidates',  # our app
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

ROOT_URLCONF = 'election_site.urls'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'home'
LOGIN_URL = 'login'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # DIRS must NOT contain absolute paths like C:\\Users\\...
        # Use BASE_DIR / 'templates' if you need a project-level template directory.
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

WSGI_APPLICATION = 'election_site.wsgi.application'


# =========================================================================
# 3. DATABASE CONFIGURATION (Consolidated for Local/Production)
# =========================================================================

# The default database is SQLite for local development.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Overwrite default with PostgreSQL config if DATABASE_URL is found (i.e., in production)
if os.environ.get('DATABASE_URL'):
    DATABASES['default'] = dj_database_url.config(
        default=os.environ.get('DATABASE_URL'), # Use the env var explicitly
        conn_max_age=600,
        conn_health_checks=True,
        ssl_require=True,
    )

# CRITICAL SECURITY/STABILITY CHECK: Ensure SQLite is not used in production
if not DEBUG and DATABASES['default']['ENGINE'] == 'django.db.backends.sqlite3':
    raise ImproperlyConfigured(
        "DATABASE_URL environment variable is NOT set. The application is trying "
        "to use ephemeral SQLite in production (DEBUG=False). Please configure "
        "DATABASE_URL with your PostgreSQL connection string."
    )


# =========================================================================
# 4. STATIC AND MEDIA FILES CONFIGURATION (WhiteNoise)
# =========================================================================

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
# Use WhiteNoise storage for handling static files in production
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# =========================================================================
# 5. OTHER DEFAULT AND THIRD-PARTY SETTINGS
# =========================================================================

# Password validation (Default validators)
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# CKEDITOR CONFIGURATION
CKEDITOR_UPLOAD_PATH = 'uploads/'
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
        'height': 300,
        'width': '100%', # Changed fixed width to 100% for better responsiveness
    },
}


LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
