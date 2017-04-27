#!/usr/bin/env python3
import os
import argparse
import logging
import time

import gevent
import connexion

from app.config import RUN_UPDATER, UPDATER_INTERVAL
from app import app, SERVER

from app.libs.resolver import get_resource_handler
from app.resources.sli.updater import update_all_indicators


logger = logging.getLogger(__name__)

SWAGGER_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'swagger.yaml')


def run_updater(once=False):
    while True:
        try:
            logger.info('Updating all indicators ...')

            update_all_indicators()

            if once:
                logger.info('Completed running the updater once. Now terminating!')
                return
        except:
            logger.exception('Updater failed!')

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
        app.add_api(SWAGGER_PATH, resolver=connexion.Resolver(function_resolver=get_resource_handler))

        app.run(port=8080, server=SERVER)
    else:
        logger.info('Running SLI updater ...')
        run_updater(args.once)


if __name__ == '__main__':
    run()
