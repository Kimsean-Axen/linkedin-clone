import os
import dj_database_url
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Load variables from a .env file (in the same folder as manage.py) into
# the environment, so EMAIL_HOST_USER / EMAIL_HOST_PASSWORD etc. don't have
# to be retyped every time a new terminal is opened.
load_dotenv(BASE_DIR / '.env')

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-change-this-in-production-use-env-variable')

DEBUG = os.environ.get('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '127.0.0.1,localhost').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'crispy_bootstrap5',
    'linkedin_app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'linkedin_clone.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'linkedin_app.context_processors.nav_badges',
            ],
        },
    },
]

WSGI_APPLICATION = 'linkedin_clone.wsgi.application'

DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Phnom_Penh'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/feed/'
LOGOUT_REDIRECT_URL = '/login/'

CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

# ── Email ────────────────────────────────────────────────────────────────────
#
# HOW TO ENABLE REAL EMAIL (verification codes sent to users):
#
#   Option A — Gmail (recommended for quick setup):
#     1. Go to your Google Account → Security → 2-Step Verification → ON
#     2. Then go to Security → App Passwords → create one for "Mail"
#     3. Set these environment variables (or create a .env file):
#
#        EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
#        EMAIL_HOST=smtp.gmail.com
#        EMAIL_PORT=587
#        EMAIL_USE_TLS=True
#        EMAIL_HOST_USER=your_gmail@gmail.com
#        EMAIL_HOST_PASSWORD=your_16_char_app_password
#        DEFAULT_FROM_EMAIL=LinkedIn Clone <your_gmail@gmail.com>
#
#   Option B — Outlook / Hotmail:
#        EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
#        EMAIL_HOST=smtp.office365.com
#        EMAIL_PORT=587
#        EMAIL_USE_TLS=True
#        EMAIL_HOST_USER=your_email@outlook.com
#        EMAIL_HOST_PASSWORD=your_password
#        DEFAULT_FROM_EMAIL=LinkedIn Clone <your_email@outlook.com>
#
#   Development fallback (no env vars set):
#     Verification codes are printed to the terminal/server console.
#     Check the terminal window where you ran `python manage.py runserver`.
#
EMAIL_BACKEND = os.environ.get(
    'EMAIL_BACKEND',
    'django.core.mail.backends.console.EmailBackend',
)
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'LinkedIn Clone <noreply@linkedinclone.com>')
RESEND_API_KEY = os.environ.get('RESEND_API_KEY', '')