#!/usr/bin/env python3
from urllib.parse import urljoin

import zign.api

from flask import request, session, redirect
from flask_oauthlib.client import OAuth

from app import connexion_app
from app.libs.oauth import get_auth_app
from app.config import APP_URL, OAUTH2_ENABLED, PRESHARED_TOKEN


# OAUTH setup
oauth = OAuth(connexion_app.app)
auth = get_auth_app(oauth)
oauth.remote_apps['auth'] = auth


def login():
    redirect_uri = urljoin(APP_URL, '/login/authorized')
    if not OAUTH2_ENABLED:
        return redirect(redirect_uri)
    return auth.authorize(callback=redirect_uri)


def logout():
    session.pop('auth_token', None)
    return redirect(urljoin(APP_URL, '/'))


def authorized():
    token = ''
    if not OAUTH2_ENABLED:
        token = PRESHARED_TOKEN or zign.api.get_token('uid', ['uid'])
    else:
        resp = auth.authorized_response()
        if resp is None:
            return 'Access denied: reason={} error={}'.format(request.args['error'], request.args['error_description'])

        if not isinstance(resp, dict):
            return 'Invalid OAUTH response'

        token = resp['access_token']

    session['auth_token'] = token
    return redirect(urljoin(APP_URL, '/'))


ROUTES = {
    '/login': login,
    '/logout': logout,
    '/login/authorized': authorized
}
