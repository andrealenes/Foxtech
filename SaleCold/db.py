import os
from decouple import config

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SQLITE = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3')
    }
}

POSTGRESQL = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'SaleCold',
        'USER': 'postgres',
        'PASSWORD': config('PASSWORD_POSTGRESQL'),
        'HOST': 'localhost',
        'PORT': '5432'
    }
}

# MYSQL = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'SaleCold',
#         'USER': config('USER_AZURE_MYSQL'),
#         'PASSWORD': config('PASSWORD_AZURE_MYSQL'),
#         'HOST': config('HOST_AZURE_MYSQL'),
#         'PORT': '3306'
#     }
# }