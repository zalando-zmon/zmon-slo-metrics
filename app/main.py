#!/usr/bin/env python3
import os
import argparse
import logging
import time

import gevent
import connexion
import zign.api

from urllib.parse import urljoin

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cache import Cache
from flask_oauthlib.client import OAuth
from flask_session import Session

from flask import request, session, redirect

from app import connexion_app, SERVER
from app.config import CACHE_TYPE, CACHE_THRESHOLD, APP_SESSION_SECRET
from app.config import RUN_UPDATER, UPDATER_INTERVAL, AUTHORIZE_URL, APP_URL, OAUTH2_ENABLED, API_PREFIX

from app.libs.oauth import OAuthRemoteAppWithRefresh, verify_oauth_with_session

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

logger = logging.getLogger(__name__)

SWAGGER_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'swagger.yaml')

# OAUTH setup
oauth = OAuth(application)
auth = OAuthRemoteAppWithRefresh(
    oauth,
    'auth',
    request_token_url=None,
    access_token_method='POST',
    access_token_url=os.getenv('ACCESS_TOKEN_URL'),
    authorize_url=AUTHORIZE_URL
)
oauth.remote_apps['auth'] = auth


@application.before_request
def process_request():
    """
    Process request.

    - Set api_url

    """
    base_url = request.base_url

    referrer = request.headers.get('referer')

    if referrer and request.url_root != referrer:
        # we use referrer as base url
        base_url = referrer
    elif APP_URL:
        base_url = APP_URL

    # Used in building full URIs
    request.api_url = urljoin(base_url, API_PREFIX + '/')


# PATHS
@application.route('/login')
def login():
    redirect_uri = urljoin(APP_URL, '/login/authorized')
    if not OAUTH2_ENABLED:
        return redirect(redirect_uri)
    return auth.authorize(callback=redirect_uri)


@application.route('/logout')
def logout():
    session.pop('auth_token', None)
    return redirect(urljoin(APP_URL, '/'))


@application.route('/login/authorized')
def authorized():
    token = ''
    if not OAUTH2_ENABLED:
        token = zign.api.get_token('uid', ['uid'])
    else:
        resp = auth.authorized_response()
        if resp is None:
            return 'Access denied: reason={} error={}'.format(request.args['error'], request.args['error_description'])

        if not isinstance(resp, dict):
            return 'Invalid OAUTH response'

        token = resp['access_token']

    session['auth_token'] = token
    return redirect(urljoin(APP_URL, '/'))


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

        connexion_app.run(port=8080, server=SERVER)
    else:
        logger.info('Running SLI updater ...')
        run_updater(args.once)


if __name__ == '__main__':
    run()
