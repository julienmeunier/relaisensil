"""
Django settings for engine project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/

Devel setting used when ./manage.py runserver is called
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY=change_me

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
TEMPLATE_DEBUG = True
ALLOWED_HOSTS = []

# Application definition
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'relais',  # Relais App
    'south',  # Migration App
    'captcha',  # Security for Relais Form
    'paypal.standard.ipn',  # Paypal App
)
MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'engine.urls'
WSGI_APPLICATION = 'engine.wsgi.application'
PROJECT_ROOT = os.path.realpath(os.path.dirname(__file__))

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/
LANGUAGE_CODE = 'fr'
LOCALE_PATHS = ['%s/conf/locale' % BASE_DIR]
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "static")  # Absolute path to the directory
STATICFILES_DIRS = ()

# Migration module
SOUTH_MIGRATION_MODULES = {
    'captcha': 'captcha.south_migrations',
}

# Paypal setting
PAYPAL_RECEIVER_EMAIL = "webmaster-test@relaisensil.com"
PAYPAL_TEST = True

#------------------------------------------------------------------------------
# Email setting
# Send fake mail on console
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEVELOPPER_MAIL = 'julien.meunier.perso@gmail.com'  # For CC in mail
