from flask import session, request, make_response, jsonify
from flask_limiter import Limiter

from app import connexion_app


def get_limiter_key():
    # First, from request
    if hasattr(request, 'token_info'):
        return request.token_info['access_token']

    # Next, session token
    token = session.get('auth_token')
    if token:
        return token

    # Next, from auth headers
    auth_headers = request.headers.get('Authorization', '')
    if auth_headers:
        _, token = auth_headers.split()

        if token:
            return token

    # Next, forwarded for ip
    forwarded_for = request.headers.get('x-forwarded-for')
    if forwarded_for:
        return forwarded_for

    # Last, from remote address
    return request.remote_addr


@connexion_app.app.errorhandler(429)
def rate_limit_exceeded(e):
    return make_response(jsonify(title='Rate limit exceeded', detail='Rate limit exceeded. Too many requests'), 429)


limiter = Limiter(key_func=get_limiter_key)
