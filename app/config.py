import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

DEBUG = os.getenv('DEBUG', False)

# DB
SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI')
SQLALCHEMY_POOL_SIZE = os.getenv('DATABASE_POOL_SIZE', 30)

# We can use signals to track changes to models (e.g Logs with username)
SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv('DATABASE_TRACK_MODIFICATIONS', True)

# API
API_AUTHORIZATION = os.getenv('SLR_API_AUTHORIZATION', '')

API_DEFAULT_LIMIT = os.getenv('API_DEFAULT_LIMIT', 100)

# ZMON
KAIROSDB_URL = os.getenv('KAIROSDB_URL')
KAIROS_QUERY_LIMIT = os.getenv('KAIROS_QUERY_LIMIT', 10000)
