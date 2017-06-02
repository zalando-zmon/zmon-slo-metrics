import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

DEBUG = os.getenv('DEBUG', False)

RUN_UPDATER = os.environ.get('SLR_RUN_UPDATER', False)

# DB
SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI')
SQLALCHEMY_POOL_SIZE = os.getenv('DATABASE_POOL_SIZE', 30)

# We can use signals to track changes to models (e.g Logs with username)
SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv('DATABASE_TRACK_MODIFICATIONS', True)

# CACHE
CACHE_TYPE = os.getenv('SLR_CACHE_TYPE', 'simple')
CACHE_KEY_PREFIX = 'SLR_'
CACHE_THRESHOLD = os.getenv('CACHE_THRESHOLD', 4096)

# AUTH
API_AUTHORIZATION = os.getenv('SLR_API_AUTHORIZATION', '')

ADMINS = os.getenv('SLR_ADMINS', [])

# COMMUNITY AUTH
API_AUTHORIZATION_COMMUNITY_URL = os.getenv('SLR_API_AUTHORIZATION_COMMUNITY_URL', '')
API_AUTHORIZATION_COMMUNITY_PREFIX = os.getenv('SLR_API_AUTHORIZATION_COMMUNITY_PREFIX', 'Functions/Communities/')

API_DEFAULT_LIMIT = os.getenv('API_DEFAULT_LIMIT', 100)

# ZMON
KAIROSDB_URL = os.getenv('KAIROSDB_URL')
KAIROS_QUERY_LIMIT = os.getenv('KAIROS_QUERY_LIMIT', 10000)

# UPDATER
MAX_QUERY_TIME_SLICE = os.getenv('MAX_QUERY_TIME_SLICE', 1440)

# Careful with high concurrency, as we might hit rate limits on ZMON
UPDATER_CONCURRENCY = os.getenv('UPDATER_CONCURRENCY', 20)
UPDATER_INTERVAL = os.getenv('UPDATER_INTERVAL', 600)
