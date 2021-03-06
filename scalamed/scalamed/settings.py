"""
Django settings for scalamed project.

Generated by 'django-admin startproject' using Django 1.11.4.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'sth2xr)1fq=2@rvonjz05079jlu=3s2z-d2l8o052dbz#(ur40'

# Get tokens from the environment variables

T1_EXP = os.environ.get('T1EXP')
T0_EXP = os.environ.get('T0EXP')

try:
    if not T1_EXP:
        print("No t1 expiry, using default")
        T1_EXP = 1
    else:
        T1_EXP = int(T1_EXP)
except ValueError:
    print("Invalid T1 Expiry")
    T1_EXP = 1

try:
    if not T0_EXP:
        print("No t0 expiry, using default")
        T0_EXP = 24
    else:
        T0_EXP = int(T0_EXP)
except ValueError:
    print("Invalid T0 Expiry")
    T0_EXP = 1

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'suit',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'authservice',
    'import_export',
    'rest_framework',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'scalamed.urls'

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

WSGI_APPLICATION = 'scalamed.wsgi.application'


# Password Hashing
# https://docs.djangoproject.com/en/1.11/topics/auth/passwords/#using-bcrypt-with-django

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
]


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTHENTICATION_BACKENDS = ['authservice.backends.EmailBackend']

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'

AUTH_USER_MODEL = 'authservice.User'

SUIT_CONFIG = {
    'ADMIN_NAME': 'ScalaMed Authentication Service',
}

_megabytes = 1024 * 1024

# Logging configuration which will be passed to LOGGING_CONFIG which defaults to
# logging.config.dictConfig(...); the schema is defined here:
# docs.python.org/3/library/logging.config.html#logging-config-dictschema
LOGGING = {
    # version of the dictConfig schema
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '[%(asctime)s][%(levelname)s][%(name)s]: %(message)s',
            'datefmt': '%Y-%m-%dT%H:%M:%S%z',
        },
    },
    'filters': {
        'main_filter': {
            'name': 'scalamed'
        }
    },
    'handlers': {

        # Log to STDOUT
        'default': {
            'level': 'DEBUG',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
            'filters': ['main_filter']
        },

        # Includes all logs 'WARNING' and above
        #'default_file': {
        #    'level': 'WARNING',
        #    'formatter': 'standard',
        #    'class': 'logging.handlers.RotatingFileHandler',
        #    'filename': 'logs/error.log',
        #    'filters': ['main_filter'],
        #    'maxBytes': 256 * _megabytes,
        #    'backupCount': 9,
        #},

        # Includes only logging from this project
        #'debug_file': {
        #    'level': 'DEBUG',
        #    'formatter': 'standard',
        #    'class': 'logging.handlers.RotatingFileHandler',
        #    'filters': ['main_filter'],
        #    'filename': 'logs/debug.log',
        #    'maxBytes': 256 * _megabytes,
        #    'backupCount': 9,
        #},

    },
    'loggers': {
        '': {
            'handlers': [
                'default',
                #'default_file',
                #'debug_file'
            ],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
