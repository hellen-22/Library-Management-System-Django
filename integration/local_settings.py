"""Optional loopback-only SQLite development settings; original PostgreSQL settings remain available."""
import os
from pathlib import Path
# core.settings reads these before this optional local database override.
for name in ('POSTGRES_DB','POSTGRES_USER','POSTGRES_PASSWORD','POSTGRES_HOST','POSTGRES_PORT'):
    os.environ.setdefault(name, 'unused')
from core.settings import *
DATABASES = {'default': {'ENGINE':'django.db.backends.sqlite3', 'NAME':os.environ.get('PRIVACY_DATABASE_PATH', str(BASE_DIR/'db.sqlite3'))}}
DEBUG = True
ALLOWED_HOSTS = ['127.0.0.1','localhost']
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
