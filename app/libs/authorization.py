from flask import request  # noqa

from app.config import API_AUTHORIZATION


def get_authorization():
    if API_AUTHORIZATION.lower() == 'community':
        return CommunityAuthorization()
    else:
        return Authorization()


class Authorization:
    def read(self, obj, **kwargs):
        return True

    def create(self, obj, **kwargs):
        return True

    def update(self, obj, **kwargs):
        return True

    def delete(self, obj, **kwargs):
        return True


class CommunityAuthorization(Authorization):
    def create(self, obj, **kwargs):
        return True

    def update(self, obj, **kwargs):
        return True

    def delete(self, obj, **kwargs):
        return True
