from urllib.parse import urljoin

from flask import request

from app.libs.resource import ResourceHandler


class APIRoot(ResourceHandler):

    @classmethod
    def get(cls, **kwargs) -> dict:
        return {
            'health_uri': urljoin(request.api_url, 'health'),
            'product_groups_uri': urljoin(request.api_url, 'product-groups'),
            'products_uri': urljoin(request.api_url, 'products'),
        }

    @classmethod
    def health(cls, **kwargs) -> dict:
        return {}, 200
