import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'dev-secret-key-change-in-production')

DEBUG = os.environ.get('DEBUG', 'False') == 'True'

IBM_HOST = os.environ.get('IBM_HOST', '')

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '.mybluemix.net',        # IBM Cloud Foundry
    '.appdomain.cloud',      # IBM Code Engine
    '.onrender.com',         # Render
]
if IBM_HOST:
    ALLOWED_HOSTS.append(IBM_HOST)


INSTALLED_APPS = [
    'django.contrib.staticfiles',
    'corsheaders',
    'api',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'fitnutribuddy.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
            ],
        },
    },
]

WSGI_APPLICATION = 'fitnutribuddy.wsgi.application'

# No database needed for this app
DATABASES = {}
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# CORS — allow frontend to call API
CORS_ALLOW_ALL_ORIGINS = DEBUG
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]
if IBM_HOST:
    CORS_ALLOWED_ORIGINS.append(f"https://{IBM_HOST}")


# Watsonx AI Configuration
WATSONX_APIKEY = os.environ.get('WATSONX_APIKEY', '')
WATSONX_PROJECT_ID = os.environ.get('WATSONX_PROJECT_ID', '')
WATSONX_URL = os.environ.get('WATSONX_URL', 'https://au-syd.ml.cloud.ibm.com')


# CSRF trusted origins for IBM Cloud and Render
CSRF_TRUSTED_ORIGINS = [
    'https://*.mybluemix.net',
    'https://*.appdomain.cloud',
    'https://*.onrender.com',
]
