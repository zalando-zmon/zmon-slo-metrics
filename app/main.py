#!/usr/bin/env python3
from opentracing_utils import trace_requests
trace_requests()  # noqa

import os
import argparse
import logging
import time

import gevent
import flask
import connexion
import opentracing

from app import SERVER
from app import level as DEBUG_LEVEL
from app.config import RUN_UPDATER, UPDATER_INTERVAL, APP_SESSION_SECRET
from app.config import CACHE_TYPE, CACHE_THRESHOLD
from app.config import OPENTRACING_TRACER, OPENTRACING_TRACER_SERVICE_NAME

from app.libs.oauth import verify_oauth_with_session
from app.utils import DecimalEncoder

from app.extensions import db, migrate, cache, session, limiter, oauth, trace_flask

from app.libs.resolver import get_resource_handler
from app.resources.sli.updater import update_all_indicators

# Models
from app.resources import ProductGroup, Product, Target, Objective, Indicator, IndicatorValue  # noqa
from app.routes import ROUTES, process_request, rate_limit_exceeded

import connexion.decorators.security
import connexion.operation
# MONKEYPATCH CONNEXION
connexion.decorators.security.verify_oauth = verify_oauth_with_session
connexion.operation.verify_oauth = verify_oauth_with_session

logger = logging.getLogger(__name__)

SWAGGER_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'swagger.yaml')


def create_app(*args, **kwargs):
    connexion_app = connexion.App(__name__)
    connexion_app.app.json_encoder = DecimalEncoder

    connexion_app.app.config.from_object('app.config')

    app = connexion_app.app

    register_extensions(app)
    register_middleware(app)
    register_routes(connexion_app)
    register_errors(app)

    if kwargs.get('connexion_app'):
        return connexion_app

    return app


def register_extensions(app: flask.Flask) -> None:
    app.secret_key = APP_SESSION_SECRET

    db.init_app(app)
    migrate.init_app(app, db)
    cache.init_app(app, config={'CACHE_TYPE': CACHE_TYPE, 'CACHE_THRESHOLD': CACHE_THRESHOLD})
    limiter.init_app(app)
    session.init_app(app)
    oauth.init_app(app)

    trace_flask(
        app, tracer_name=OPENTRACING_TRACER, service_name=OPENTRACING_TRACER_SERVICE_NAME, debug_level=DEBUG_LEVEL)


def register_middleware(app: flask.Flask) -> None:
    # Add middleware processors
    app.before_request(process_request)


def register_api(connexion_app: connexion.App) -> None:
    # IMPORTANT: Add swagger api after *db* instance is ready!
    connexion_app.add_api(SWAGGER_PATH, resolver=connexion.Resolver(function_resolver=get_resource_handler))


def register_routes(connexion_app: connexion.App) -> None:
    # Add extra routes
    for rule, handler in ROUTES.items():
        connexion_app.add_url_rule(rule, view_func=handler)


def register_errors(app: flask.Flask) -> None:
    app.errorhandler(429)(rate_limit_exceeded)


def run_updater(app: flask.Flask, once=False):
    with app.app_context():
        try:
            # TODO: HACK! remove when done!
            while True:
                seconds = 5
                while seconds:
                    try:
                        if opentracing.tracer.sensor.agent.fsm.fsm.current == "good2go":
                            logger.info('Tracer is ready and announced!')
                            break
                        seconds -= 1
                        time.sleep(1)
                    except:
                        break

                updater_span = opentracing.tracer.start_span(operation_name='slr-updater')

                with updater_span:
                    try:
                        logger.info('Updating all indicators ...')

                        update_all_indicators(app, parent_span=updater_span)
                    except:
                        updater_span.set_tag('updater-status', 'Failed')
                        logger.exception('Updater failed!')
                    else:
                        updater_span.set_tag('updater-status', 'Succeeded')

                    if once:
                        logger.info('Completed running the updater once. Now terminating!')
                        updater_span.set_tag('updater-run-once', 'True')
                        return

                logger.info('Completed running the updater. Sleeping for {} minutes!'.format(UPDATER_INTERVAL // 60))

                time.sleep(UPDATER_INTERVAL)
        except KeyboardInterrupt:
            logger.info('Terminating updater in response to KeyboardInterrupt!')


def run():
    argp = argparse.ArgumentParser(description='Service level reports application')
    argp.add_argument('--with-updater', dest='with_updater', action='store_true', help='Run server with updater!')
    argp.add_argument('-u', '--updater-only', dest='updater', action='store_true', help='Run the updater only!')
    argp.add_argument(
        '-o', '--once', dest='once', action='store_true',
        help='Make sure the updater runs once and exits! Only works if --updater-only is used, ignored otherwise')

    args = argp.parse_args()

    connexion_app = create_app(connexion_app=True)

    if not args.updater:
        if args.with_updater or RUN_UPDATER:
            logger.info('Running SLI updater ...')
            gevent.spawn(run_updater, connexion_app.app)

        # run our standalone gevent server
        logger.info('Service level reports starting application server')

        register_api(connexion_app)

        # Start the server
        try:
            connexion_app.run(port=8080, server=SERVER)
        except KeyboardInterrupt:
            logger.info('KeyboardInterrupt ... terminating server!')
    else:
        logger.info('Running SLI updater ...')
        run_updater(connexion_app.app, args.once)


# set the WSGI application callable to allow using uWSGI:
# uwsgi --http :8080 -w app
application = create_app()


if __name__ == '__main__':
    run()
