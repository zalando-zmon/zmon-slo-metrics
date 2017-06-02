#!/usr/bin/env python3
from gevent import os

SERVER = None  # noqa

if not os.environ.get('SLR_LOCAL_ENV'):  # noqa
    import gevent.monkey

    gevent.monkey.patch_all()

    import psycogreen.gevent
    psycogreen.gevent.patch_psycopg()

    SERVER = 'gevent'

import logging
import warnings

from flask.exthook import ExtDeprecationWarning
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

warnings.filterwarnings('ignore', category=ExtDeprecationWarning)  # noqa

from flask_cache import Cache

import connexion

from app.config import DEBUG, CACHE_TYPE, CACHE_THRESHOLD
from app.utils import DecimalEncoder

__version__ = '0.1'

level = logging.INFO if not DEBUG else logging.DEBUG
logging.basicConfig(level=level)

app = connexion.App(__name__)
app.app.json_encoder = DecimalEncoder

app.app.config.from_object('app.config')

# set the WSGI application callable to allow using uWSGI:
# uwsgi --http :8080 -w app
application = app.app

# DB
db = SQLAlchemy(application)

# CACHE
cache = Cache(application, config={'CACHE_TYPE': CACHE_TYPE, 'CACHE_THRESHOLD': CACHE_THRESHOLD})

# Models
from app.resources import ProductGroup, Product, Target, Objective, Indicator, IndicatorValue  # noqa

migrate = Migrate(application, db)
