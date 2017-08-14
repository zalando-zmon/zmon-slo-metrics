from flask import session, request
from flask_limiter import Limiter


def get_limiter_key():
    # Next, from auth headers
    auth_headers = request.headers.get('Authorization', '')
    if auth_headers:
        _, token = auth_headers.split()

        if token:
            return token

    # Next, session token
    user = session.get('user')
    if user:
        return user

    # Next, forwarded for ip
    forwarded_for = request.headers.get('x-forwarded-for')
    if forwarded_for:
        return forwarded_for

    # Last, from remote address
    return request.remote_addr


limiter = Limiter(key_func=get_limiter_key)
