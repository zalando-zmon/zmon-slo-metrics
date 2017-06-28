#!/usr/bin/env python3

import os
import sys
import time
import logging
import subprocess

from sqlalchemy_utils.functions import database_exists, create_database


MAX_RETRIES = 5

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

logger.addHandler(logging.StreamHandler(sys.stdout))


def upgrade(path):
    try:
        result = subprocess.check_output(['flask', 'db', 'upgrade', '-d', path], stderr=subprocess.STDOUT)
        for r in result.splitlines():
            print(r)
    except subprocess.CalledProcessError as e:
        return e.returncode

    return 0


def main():
    retries = MAX_RETRIES

    database_uri = os.environ.get('DATABASE_URI')
    if not database_uri:
        logger.error('Migration cannot proceed. Please specify full DATABASE_URI.')
        sys.exit(1)

    migration_path = os.environ.get('DATABASE_MIGRATIONS', '/app/migrations')

    logger.info('Preparing for migration...')

    time.sleep(1)

    while retries:
        try:
            logger.info('Creating database ...')

            if not database_exists(database_uri):
                create_database(database_uri)

                logger.info('Database created!')
            else:
                logger.info('Database exists!')

            logger.info('Upgrading database ...')

            if upgrade(migration_path):
                logger.error('Failed to upgrade')
                sys.exit(1)

            logger.info('Done!')

            sys.exit(0)
        except KeyboardInterrupt:
            sys.exit(0)
        except Exception as e:
            logger.error(e)
            retries -= 1
            time.sleep(2)

    logger.error('Failed to migrate')
    sys.exit(1)


if __name__ == '__main__':
    main()
