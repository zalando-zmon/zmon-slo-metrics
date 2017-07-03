from app.config import API_AUTHORIZATION

from .simple import Authorization
from .community import CommunityAuthorization


def get_authorization() -> Authorization:
    if API_AUTHORIZATION.lower() == 'community':
        return CommunityAuthorization()
    else:
        return Authorization()


__all__ = (
    'Authorization',
    'CommunityAuthorization',
    'get_authorization',
)
