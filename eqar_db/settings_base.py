import ldap
import os

from pathlib import Path

from django_auth_ldap.config import LDAPSearch, PosixGroupType

from corsheaders.defaults import default_headers

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

ALLOWED_HOSTS = [
    'localhost',
    'testing.int.eqar.eu',
    'django.testzone.eqar.eu'
]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework.authtoken',
    'django_filters',
    'drf_yasg',
    'corsheaders',

    'uni_db',

    'contacts',
    'members',
    'agencies',
    'ldap_view',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_HEADERS = list(default_headers) + [
    "if-modified-since",
]

AUTH_LDAP_SERVER_URI = 'ldap://ldap.int.eqar.eu/'

AUTH_LDAP_BIND_DN = ''
AUTH_LDAP_BIND_PASSWORD = ''
AUTH_LDAP_USER_SEARCH = LDAPSearch(
    'ou=users,dc=eqar,dc=eu',
    ldap.SCOPE_SUBTREE,
    '(uid=%(user)s)',
)
# Or:
# AUTH_LDAP_USER_DN_TEMPLATE = 'uid=%(user)s,ou=users,dc=example,dc=com'

# Set up the basic group parameters.
AUTH_LDAP_GROUP_SEARCH = LDAPSearch(
    'ou=users,dc=eqar,dc=eu',
    ldap.SCOPE_SUBTREE,
    '(objectClass=posixGroup)',
)
AUTH_LDAP_GROUP_TYPE = PosixGroupType()

# Simple group restrictions
#AUTH_LDAP_REQUIRE_GROUP = 'cn=enabled,ou=django,ou=groups,dc=example,dc=com'
#AUTH_LDAP_DENY_GROUP = 'cn=disabled,ou=django,ou=groups,dc=example,dc=com'

# Populate the Django user from the LDAP directory.
AUTH_LDAP_USER_ATTR_MAP = {
    'first_name': 'givenName',
    'last_name': 'sn',
    'email': 'mail',
}

AUTH_LDAP_USER_FLAGS_BY_GROUP = {
#    'is_active': 'cn=active,ou=django,ou=groups,dc=example,dc=com',
    'is_staff': (
        'cn=eqar,ou=users,dc=eqar,dc=eu',
        'cn=externals,ou=users,dc=eqar,dc=eu',
        'cn=eqarrc,ou=users,dc=eqar,dc=eu',
        'cn=eqareb,ou=users,dc=eqar,dc=eu',
        'cn=eqarac,ou=users,dc=eqar,dc=eu',
    ),
    'is_superuser': 'cn=eqar,ou=users,dc=eqar,dc=eu',
}

# This is the default, but I like to be explicit.
AUTH_LDAP_ALWAYS_UPDATE_USER = True

# Use LDAP group membership to calculate group permissions.
AUTH_LDAP_FIND_GROUP_PERMS = True

# Cache distinguished names and group memberships for an hour to minimize
# LDAP traffic.
AUTH_LDAP_CACHE_TIMEOUT = 30

# Keep ModelBackend around for per-user permissions and maybe a local
# superuser.
AUTHENTICATION_BACKENDS = [
    'django_auth_ldap.backend.LDAPBackend',
    'django.contrib.auth.backends.ModelBackend',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'eqar_db.authentication.BearerAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
        'rest_framework_csv.renderers.PaginatedCSVRenderer',
    ),
#    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.NamespaceVersioning',
    'DEFAULT_PAGINATION_CLASS': 'uni_db.filters.SearchFacetPagination',
    'PAGE_SIZE': 10,
}


ROOT_URLCONF = 'eqar_db.urls'

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

WSGI_APPLICATION = 'eqar_db.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': '/var/run/mysqld/mysqld.sock',
        'NAME': 'eqar',
    }
}

# DEQAR URL and token to be set in environment
DEQAR_BASE = os.environ['DEQAR_BASE'] if 'DEQAR_BASE' in os.environ else None
DEQAR_TOKEN = os.environ['DEQAR_TOKEN'] if 'DEQAR_TOKEN' in os.environ else None

# application title
UNI_DB_TITLE = "EQAR database - TEST"

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-gb'

TIME_ZONE = 'Europe/Ljubljana'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR.parent / 'static'
]

