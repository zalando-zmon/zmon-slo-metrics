#!/usr/bin/env python3
import os
import argparse
import logging
import time

import gevent
import connexion


from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cache import Cache
from flask_session import Session

from app import connexion_app, SERVER
from app.config import CACHE_TYPE, CACHE_THRESHOLD, APP_SESSION_SECRET
from app.config import RUN_UPDATER, UPDATER_INTERVAL

from app.libs.oauth import verify_oauth_with_session

import connexion.decorators.security
import connexion.operation
# MONKEYPATCH CONNEXION
connexion.decorators.security.verify_oauth = verify_oauth_with_session
connexion.operation.verify_oauth = verify_oauth_with_session  # noqa


# set the WSGI application callable to allow using uWSGI:
# uwsgi --http :8080 -w app
application = connexion_app.app

# DB
db = SQLAlchemy(application)

# CACHE
cache = Cache(application, config={'CACHE_TYPE': CACHE_TYPE, 'CACHE_THRESHOLD': CACHE_THRESHOLD})

# SESSION
Session(application)
application.secret_key = APP_SESSION_SECRET

# Models
from app.resources import ProductGroup, Product, Target, Objective, Indicator, IndicatorValue  # noqa

migrate = Migrate(application, db)

from app.libs.resolver import get_resource_handler  # noqa
from app.resources.sli.updater import update_all_indicators  # noqa

from app.routes import ROUTES, process_request  # noqa

logger = logging.getLogger(__name__)

SWAGGER_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'swagger.yaml')


def run_updater(once=False):
    while True:
        try:
            logger.info('Updating all indicators ...')

            update_all_indicators()
        except:
            logger.exception('Updater failed!')

        if once:
            logger.info('Completed running the updater once. Now terminating!')
            return

        logger.info('Completed running the updater. Sleeping for {} minutes!'.format(UPDATER_INTERVAL // 60))

        time.sleep(UPDATER_INTERVAL)


def run():
    argp = argparse.ArgumentParser(description='Service level reports application')
    argp.add_argument('--with-updater', dest='with_updater', action='store_true', help='Run server with updater!')
    argp.add_argument('-u', '--updater-only', dest='updater', action='store_true', help='Run the updater only!')
    argp.add_argument(
        '-o', '--once', dest='once', action='store_true',
        help='Make sure the updater runs once and exits! Only works if --updater-only is used, ignored otherwise')

    args = argp.parse_args()

    if not args.updater:
        if args.with_updater or RUN_UPDATER:
            logger.info('Running SLI updater ...')
            gevent.spawn(run_updater)

        # run our standalone gevent server
        logger.info('Service level reports starting application server')

        # IMPORTANT: Add swagger api after *db* instance is ready!
        connexion_app.add_api(SWAGGER_PATH, resolver=connexion.Resolver(function_resolver=get_resource_handler))

        # Add extra routes
        for rule, handler in ROUTES.items():
            connexion_app.add_url_rule(rule, view_func=handler)

        # Add middleware processors
        application.before_request(process_request)

        # Start the server
        connexion_app.run(port=8080, server=SERVER)
    else:
        logger.info('Running SLI updater ...')
        run_updater(args.once)


if __name__ == '__main__':
    run()
