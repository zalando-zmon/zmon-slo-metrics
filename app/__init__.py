#!/usr/bin/env python3
import gevent.monkey

gevent.monkey.patch_all()  # noqa

import psycogreen.gevent
psycogreen.gevent.patch_psycopg()  # noqa

import os
import logging

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

import connexion

from app.utils import DecimalEncoder
from app.libs.resolver import get_resource_handler

__version__ = '0.1'

logging.basicConfig(level=logging.INFO)
swagger_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'swagger.yaml')

app = connexion.App(__name__)
app.app.json_encoder = DecimalEncoder

app.app.config.from_object('app.config')

# set the WSGI application callable to allow using uWSGI:
# uwsgi --http :8080 -w app
application = app.app

# DB
db = SQLAlchemy(application)

# IMPORTANT: Add swagger api after *db* instance is ready!
app.add_api(swagger_path, resolver=connexion.Resolver(function_resolver=get_resource_handler))

# Models
from app.resources import ProductGroup, Product, Target, Objective, Indicator, IndicatorValue  # noqa

migrate = Migrate(application, db)
