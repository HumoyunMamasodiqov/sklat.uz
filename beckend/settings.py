import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-0umegca*)@-jud%z(f&_e4fgitppj(&ly0gc+gwvk6)knrm56-'

# Render SERVER uchun DEBUG = False qilamiz
DEBUG = False

ALLOWED_HOSTS = [
    "sklatuz.onrender.com",
    "localhost",
    "127.0.0.1",
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

    # === Render uchun MUHIM (statiklarni chiqaradi) ===
    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'beckend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
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
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# =============== STATIC FILES (Render) ===============
STATIC_URL = '/static/'

# Local static folder (static/img, static/css ...)
STATICFILES_DIRS = [BASE_DIR / 'static']

# Serverda collectstatic natijasi shu papkaga tushadi
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise uchun maxsus storage
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# =============== MEDIA FILES (Images Upload) ===============
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# =============== DEFAULT AUTO FIELD ===============
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
