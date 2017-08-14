import logging

from urllib.parse import urljoin, urlparse, urlunparse

from flask import request
from flask import session as flask_session

from app.config import APP_URL, API_PREFIX

logger = logging.getLogger(__name__)


def process_request():
    """
    Process request.

    - Set api_url

    """
    base_url = request.base_url

    referrer = request.headers.get('referer')

    if referrer:
        # we use referrer as base url
        parts = urlparse(referrer)
        base_url = urlunparse((parts.scheme, parts.netloc, '', '', '', ''))
    elif APP_URL:
        base_url = APP_URL

    # Used in building full URIs
    request.api_url = urljoin(base_url, API_PREFIX + '/')
    logger.info('Middleware: {}'.format(flask_session.get('user')))
    request.user = flask_session.get('user')
    request.realm = flask_session.get('realm', 'employees')
