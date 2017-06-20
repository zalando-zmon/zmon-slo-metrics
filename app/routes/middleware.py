from urllib.parse import urljoin

from flask import request

from app.config import APP_URL, API_PREFIX


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
