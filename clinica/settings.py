"""
Configuración principal del Sistema de Historias Clínicas.
"""
from pathlib import Path
import os
import socket

BASE_DIR = Path(__file__).resolve().parent.parent


def env_bool(name, default=False):
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {'1', 'true', 'yes', 'on'}


def env_list(name, default=''):
    value = os.getenv(name, default)
    return [item.strip() for item in value.split(',') if item.strip()]


def env_int(name, default=0):
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


SECRET_KEY = os.getenv('CLINICA_SECRET_KEY', 'django-insecure-clinica-local-change-me-in-production')

# Para uso LAN real, dejar DEBUG apagado y cargar hosts/IPs permitidos desde entorno.
DEBUG = env_bool('CLINICA_DEBUG', False)

DEFAULT_ALLOWED_HOSTS = ['127.0.0.1', 'localhost', socket.gethostname()]
ALLOWED_HOSTS = env_list('CLINICA_ALLOWED_HOSTS', ','.join(DEFAULT_ALLOWED_HOSTS))

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Librerías de terceros
    'widget_tweaks',
    # Aplicaciones del sistema
    'cuentas',
    'pacientes',
    'consulta',
    'facturacion',
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

ROOT_URLCONF = 'clinica.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'clinica.wsgi.application'

db_engine = os.getenv('CLINICA_DB_ENGINE', 'sqlite3').strip().lower()

if db_engine == 'postgresql':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('CLINICA_DB_NAME', 'clinica'),
            'USER': os.getenv('CLINICA_DB_USER', 'postgres'),
            'PASSWORD': os.getenv('CLINICA_DB_PASSWORD', ''),
            'HOST': os.getenv('CLINICA_DB_HOST', '127.0.0.1'),
            'PORT': env_int('CLINICA_DB_PORT', 5432),
            'CONN_MAX_AGE': env_int('CLINICA_DB_CONN_MAX_AGE', 60),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
]

LANGUAGE_CODE = 'es-ar'
TIME_ZONE = 'America/Argentina/Buenos_Aires'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Autenticación
AUTH_USER_MODEL = 'cuentas.Usuario'
LOGIN_URL = '/cuentas/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/cuentas/login/'

# Roles del sistema
ROLES = {
    'ADMIN': 'admin',
    'MEDICO': 'medico',
    'RECEPCION': 'recepcion',
}

# Datos del consultorio para tickets y recetas.
CONSULTORIO = {
    'nombre': os.getenv('CLINICA_CONSULTORIO_NOMBRE', 'Consultorio Medico'),
    'direccion': os.getenv('CLINICA_CONSULTORIO_DIRECCION', 'Direccion del consultorio'),
    'telefono': os.getenv('CLINICA_CONSULTORIO_TELEFONO', 'Tel: 000-0000'),
    'email': os.getenv('CLINICA_CONSULTORIO_EMAIL', 'consultas@clinica.local'),
    'ciudad': os.getenv('CLINICA_CONSULTORIO_CIUDAD', 'Ciudad no configurada'),
    'logo': os.getenv('CLINICA_CONSULTORIO_LOGO') or None,
}

# Configuración impresora térmica (ajustar según modelo)
IMPRESORA_TERMICA = {
    'tipo': 'usb',       # 'usb', 'serial', 'network'
    'vendor': 0x04b8,    # Epson por defecto
    'product': 0x0202,
    'ancho_mm': 58,      # 58 o 80 mm
}
