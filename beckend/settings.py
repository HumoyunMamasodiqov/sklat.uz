import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-0umegca*)@-jud%z(f&_e4fgitppj(&ly0gc+gwvk6)knrm56-'

# Mahalliy ishlash uchun DEBUG=True, production uchun False
DEBUG = True  # Mahalliy test uchun True qiling

ALLOWED_HOSTS = [
    "sklatuz.onrender.com",
    "localhost",
    "127.0.0.1",
    "*",  # Barcha hostlar uchun ruxsat (test uchun)
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'frontend',  # sening apping
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    
    # WhiteNoise middleware (STATIC_ROOT bo'lsagina ishlaydi)
    'whitenoise.middleware.WhiteNoiseMiddleware',
    
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'beckend.urls'

# TEMPLATES sozlamalarini to'g'rilash
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',  # Global templates papka
        ],
        'APP_DIRS': True,  # App ichidagi templates papkasini qidirish
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',  # MUHIM: request qo'shing
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'beckend.wsgi.application'

# =============== DATABASE ===============
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# =============== PASSWORD VALIDATION ===============
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# =============== GENERAL SETTINGS ===============
LANGUAGE_CODE = 'uz'
TIME_ZONE = 'Asia/Tashkent'
USE_I18N = True
USE_TZ = True

# =============== STATIC FILES ===============
STATIC_URL = '/static/'

# Local static files
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Production uchun collectstatic papkasi
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise storage (DEBUG=False bo'lganda ishlaydi)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# =============== MEDIA FILES ===============
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# =============== DEFAULT AUTO FIELD ===============
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# =============== LOGIN/LOGOUT REDIRECTS ===============
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'

# =============== SECURITY (Production uchun) ===============
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True