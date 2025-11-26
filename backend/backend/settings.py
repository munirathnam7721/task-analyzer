# backend/backend/settings.py

import os
from pathlib import Path
import dj_database_url # Import for production database handling

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: Keep the SECRET KEY secure! Use environment variables in real deployment.
SECRET_KEY = 'django-insecure-z*m9&j3v+1m1x2q&8!&j3v+1m1x2q&8!&j3v+1m1x2q&8!&j3v+1m1x2q&8!'

# SECURITY WARNING: DEBUG must be FALSE in production
DEBUG = False

# Allowed hosts must include the deployed domains
ALLOWED_HOSTS = [
    '.render.com', 
    'task-analyzer.onrender.com', # Replace with your actual Render API domain
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'rest_framework',
    'corsheaders',

    # Local apps
    'tasks.apps.TasksConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Added for production static file serving
    
    'corsheaders.middleware.CorsMiddleware', 
    
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


ROOT_URLCONF = 'backend.urls'

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

WSGI_APPLICATION = 'backend.wsgi.application'


# Database Configuration (Uses SQLite locally, overrides with DATABASE_URL in production)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Integrate dj-database-url for production database (e.g., PostgreSQL on Render)
if os.environ.get('DATABASE_URL'):
    DATABASES['default'] = dj_database_url.config(
        conn_max_age=600, 
        conn_health_check=True
    )

# ... (rest of AUTH_PASSWORD_VALIDATORS and internationalization)

# Static files configuration for Whitenoise
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles' # Location where static files are collected

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS Configuration
CORS_ALLOWED_ORIGINS = [
    # Local Development Origins
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    
    # Production Frontend Domain (HTTPS required!)
    'https://frontend.onrender.com', # Replace with actual frontend domain
]

CORS_ALLOW_CREDENTIALS = True