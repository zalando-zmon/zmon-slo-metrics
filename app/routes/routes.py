#!/usr/bin/env python3
from urllib.parse import urljoin

import zign.api

from flask import request, redirect
from flask import session as flask_session

from app.libs.oauth import get_auth_app
from app.config import APP_URL, OAUTH2_ENABLED, PRESHARED_TOKEN

from app.extensions import set_token_info, oauth


# OAUTH setup
auth = get_auth_app(oauth)
oauth.remote_apps['auth'] = auth


def login():
    redirect_uri = urljoin(APP_URL, '/login/authorized')
    if not OAUTH2_ENABLED:
        return redirect(redirect_uri)
    return auth.authorize(callback=redirect_uri)


def logout():
    flask_session.pop('auth_token', None)
    return redirect(urljoin(APP_URL, '/'))


def authorized():
    if not OAUTH2_ENABLED:
        token_info = {'access_token': PRESHARED_TOKEN or zign.api.get_token('uid', ['uid'])}
    else:
        resp = auth.authorized_response()
        if resp is None:
            return 'Access denied: reason={} error={}'.format(request.args['error'], request.args['error_description'])

        if not isinstance(resp, dict):
            return 'Invalid OAUTH response'

        token_info = resp

    set_token_info(token_info)

    return redirect(urljoin(APP_URL, '/'))


ROUTES = {
    '/login': login,
    '/logout': logout,
    '/login/authorized': authorized
}
