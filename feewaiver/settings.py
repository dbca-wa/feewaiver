from django.core.exceptions import ImproperlyConfigured
from django.utils.log import DEFAULT_LOGGING

import os
import confy
import decouple
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
confy.read_environment_file(BASE_DIR+"/.env")
os.environ.setdefault("BASE_DIR", BASE_DIR)

from ledger.settings_base import *

ROOT_URLCONF = 'feewaiver.urls'
SITE_ID = 1
DEPT_DOMAINS = env('DEPT_DOMAINS', ['dpaw.wa.gov.au', 'dbca.wa.gov.au'])
SYSTEM_MAINTENANCE_WARNING = env('SYSTEM_MAINTENANCE_WARNING', 24) # hours
DISABLE_EMAIL = env('DISABLE_EMAIL', False)
SHOW_TESTS_URL = env('SHOW_TESTS_URL', False)
SHOW_DEBUG_TOOLBAR = env('SHOW_DEBUG_TOOLBAR', False)

if SHOW_DEBUG_TOOLBAR:

    def show_toolbar(request):
        return True

    MIDDLEWARE_CLASSES += [
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    ]
    INSTALLED_APPS += (
        'debug_toolbar',
    )
    INTERNAL_IPS = ('127.0.0.1', 'localhost')

    # this dict removes check to dtermine if toolbar should display --> works for rks docker container
    DEBUG_TOOLBAR_CONFIG = {
        "SHOW_TOOLBAR_CALLBACK" : show_toolbar,
        'INTERCEPT_REDIRECTS': False,
    }
MIDDLEWARE_CLASSES += [
    'whitenoise.middleware.WhiteNoiseMiddleware',
]
MIDDLEWARE = MIDDLEWARE_CLASSES
MIDDLEWARE_CLASSES = None

STATIC_URL = '/static/'

SHOW_ROOT_API = env('SHOW_ROOT_API', False)

INSTALLED_APPS += [
    'reversion_compare',
    # 'bootstrap3',
    'django_bootstrap5',
    'feewaiver',
    'taggit',
    'rest_framework',
    'rest_framework_datatables',
    #'rest_framework_gis',
    'reset_migrations',
    'ckeditor',
    'appmonitor_client',
    'ledger',
]

CRON_CLASSES = [
    'appmonitor_client.cron.CronJobAppMonitorClient',
]

ADD_REVERSION_ADMIN=True

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
        'rest_framework_datatables.renderers.DatatablesRenderer',
    ),
}


TEMPLATES[0]['DIRS'].append(os.path.join(BASE_DIR, 'feewaiver', 'templates'))
BOOTSTRAP3 = {
    'jquery_url': '//static.dpaw.wa.gov.au/static/libs/jquery/2.2.1/jquery.min.js',
    'base_url': '//static.dpaw.wa.gov.au/static/libs/twitter-bootstrap/3.3.6/',
    'css_url': 'ledger/css/bootstrap.min.css',
    'theme_url': None,
    'javascript_url': None,
    'javascript_in_head': False,
    'include_jquery': False,
    'required_css_class': 'required-form-field',
    'set_placeholder': False,
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': os.path.join(BASE_DIR, 'feewaiver', 'cache'),
    }
}
STATIC_ROOT=os.path.join(BASE_DIR, 'staticfiles_fw')
STATICFILES_DIRS.append(os.path.join(os.path.join(BASE_DIR, 'feewaiver', 'static')))
DEV_STATIC = env('DEV_STATIC',False)
DEV_STATIC_URL = env('DEV_STATIC_URL')
if DEV_STATIC and not DEV_STATIC_URL:
    raise ImproperlyConfigured('If running in DEV_STATIC, DEV_STATIC_URL has to be set')
DATA_UPLOAD_MAX_NUMBER_FIELDS = None
DEV_APP_BUILD_URL = env('DEV_APP_BUILD_URL')  # URL of the Dev app.js served by webpack & express

# Use git commit hash for purging cache in browser for deployment changes
GIT_COMMIT_HASH = ''
GIT_COMMIT_DATE = ''
if  os.path.isdir(BASE_DIR+'/.git/') is True:
    GIT_COMMIT_DATE = os.popen('cd '+BASE_DIR+' ; git log -1 --format=%cd').read()
    GIT_COMMIT_HASH = os.popen('cd  '+BASE_DIR+' ; git log -1 --format=%H').read()
if len(GIT_COMMIT_HASH) == 0: 
    GIT_COMMIT_HASH = os.popen('cat /app/git_hash').read()
    if len(GIT_COMMIT_HASH) == 0:
       print ("ERROR: No git hash provided")

# Department details
SYSTEM_NAME = env('SYSTEM_NAME', 'Fee waiver')
SYSTEM_NAME_SHORT = env('SYSTEM_NAME_SHORT', 'FW')
SITE_PREFIX = env('SITE_PREFIX', '')
SITE_DOMAIN = env('SITE_DOMAIN', '')
SUPPORT_EMAIL = env('SUPPORT_EMAIL', 'feewaiver@' + SITE_DOMAIN).lower()
DEP_URL = env('DEP_URL','www.' + SITE_DOMAIN)
DEP_PHONE = env('DEP_PHONE','(08) 9219 9978')
DEP_PHONE_SUPPORT = env('DEP_PHONE_SUPPORT','(08) 9219 9000')
DEP_FAX = env('DEP_FAX','(08) 9423 8242')
DEP_POSTAL = env('DEP_POSTAL','Locked Bag 104, Bentley Delivery Centre, Western Australia 6983')
DEP_NAME = env('DEP_NAME','Department of Biodiversity, Conservation and Attractions')
DEP_NAME_SHORT = env('DEP_NAME_SHORT','DBCA')
SITE_URL = env('SITE_URL', 'https://' + SITE_PREFIX + '.' + SITE_DOMAIN)
PUBLIC_URL=env('PUBLIC_URL', SITE_URL)
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', 'no-reply@' + SITE_DOMAIN).lower()
MEDIA_APP_DIR = env('MEDIA_APP_DIR', 'cols')
ADMIN_GROUP = env('ADMIN_GROUP', 'Feewaiver Admin')
CRON_RUN_AT_TIMES = env('CRON_RUN_AT_TIMES', '04:05')
CRON_EMAIL = env('CRON_EMAIL', 'cron@' + SITE_DOMAIN).lower()
EMAIL_FROM = DEFAULT_FROM_EMAIL

BASE_URL=env('BASE_URL')

CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
        'height': 300,
        'width': '100%',
    },
    'awesome_ckeditor': {
        'toolbar': 'Basic',
    },
}

if env('CONSOLE_EMAIL_BACKEND', False):
   EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

VERSION_NO='1.0.1'
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

DEFAULT_LOGGING["loggers"]["django"]["handlers"] = ["console"]  # Remove mail_admins handler, original value: ["console", "mail_admins"]

LOGGING = {
    "version": 1,
    'formatters': {
        'verbose2': {
            "format": "%(levelname)s %(asctime)s %(name)s [Line:%(lineno)s][%(funcName)s] %(message)s"
        }
    },
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose2',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'feewaiver.log'),
            'formatter': 'verbose2',
            'maxBytes': 5242880
        },
        'file_for_sql': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'feewaiver_sql.log'),
            'formatter': 'verbose2',
            'maxBytes': 5242880
        },
    },
    'loggers': {
        '': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': True
        },
        # Log SQL
        # 'django.db.backends': {
        #     'level': 'DEBUG',
        #     'handlers': ['file_for_sql'],
        #     'propagate': False,
        # },
    }
}
PAYMENT_LOGGING=env('PAYMENT_LOGGING','False')
if PAYMENT_LOGGING == 'True' or PAYMENT_LOGGING is True:
   LOGGING['loggers']['ledger_bpoint'] = { 'handlers': ['file'],'level': 'INFO', } 
CSRF_TRUSTED_ORIGINS_STRING = decouple.config("CSRF_TRUSTED_ORIGINS", default='[]')
CSRF_TRUSTED_ORIGINS = json.loads(str(CSRF_TRUSTED_ORIGINS_STRING))

# This is needed so that the chmod is not called in django/core/files/storage.py
# (_save method of FileSystemStorage class)
# As it causes a permission exception when using azure network drives
FILE_UPLOAD_PERMISSIONS = None

# Define the private media root and URL
PRIVATE_MEDIA_ROOT = os.path.join(BASE_DIR, 'private-media')
PRIVATE_MEDIA_URL = '/private-media/'
# Ensure the private media directory exists
if not os.path.exists(PRIVATE_MEDIA_ROOT):
    os.makedirs(PRIVATE_MEDIA_ROOT)
DEFAULT_FILE_STORAGE = 'feewaiver.storage.PrivateMediaStorage'

# from pprint import pprint
# print("\n=== LOGGING Configuration ===\n")
# pprint(LOGGING, indent=2, width=80)