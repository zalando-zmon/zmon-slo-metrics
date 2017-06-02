from typing import List
from urllib.parse import urljoin

from flask_sqlalchemy import BaseQuery

from connexion import ProblemException, request

from app import db
from app.libs.resource import ResourceHandler
from app.utils import slugger

from app.resources.product_group.models import ProductGroup

from .models import Product


class ProductResource(ResourceHandler):
    model_fields = ('name',)

    def get_filter_kwargs(self, **kwargs) -> dict:
        """Return relevant filters"""
        filters = {}

        if 'name' in kwargs:
            filters['name'] = kwargs['name']

        return filters

    def get_query(self, **kwargs) -> BaseQuery:
        return Product.query

    def validate(self, product: dict, **kwargs) -> None:
        if not product or not product.get('name'):
            raise ProblemException(title='Invalid product', detail="Product 'name' must have a value!")

        if not product.get('product_group_uri'):
            raise ProblemException(title='Invalid product', detail="Product 'product_group_uri' must have a value!")

    def new_object(self, product: dict, **kwargs) -> Product:
        fields = {
            'name': product['name']
        }

        product_group_id = self.get_id_from_uri(product['product_group_uri'])

        product_group = ProductGroup.query.get_or_404(product_group_id)

        fields['product_group_id'] = product_group.id

        return Product(**fields)

    def get_objects(self, query: BaseQuery, **kwargs) -> List[Product]:
        return [obj for obj in query.all()]

    def get_object(self, obj_id: int, **kwargs) -> Product:
        return Product.query.get_or_404(obj_id)

    def save_object(self, obj: Product, **kwargs) -> Product:
        db.session.add(obj)
        db.session.commit()

        return obj

    def update_object(self, obj: Product, product: dict, **kwargs) -> Product:
        obj.name = product.get('name')

        product_group_id = self.get_id_from_uri(product['product_group_uri'])

        # No need to make extra DB call!
        if obj.product_group_id != product_group_id:
            product_group = ProductGroup.query.get_or_404(product_group_id)
            obj.product_group_id = product_group.id

        db.session.commit()

        return obj

    def delete_object(self, obj: Product, **kwargs) -> None:
        db.session.delete(obj)
        db.session.commit()

    def build_resource(self, obj: Product, **kwargs) -> dict:
        resource = super().build_resource(obj)

        # extra fields
        resource['slug'] = slugger(obj.name)
        resource['product_group_name'] = obj.product_group.name

        # Links
        base_uri = resource['uri'] + '/'

        # TODO: get these from the resources as single source of truth?
        resource['product_group_uri'] = urljoin(request.url_root, 'product-groups/{}'.format(obj.product_group_id))
        resource['product_sli_uri'] = urljoin(base_uri, 'sli')
        resource['product_slo_uri'] = urljoin(base_uri, 'slo')
        resource['product_reports_uri'] = urljoin(base_uri, 'reports')
        resource['product_reports_weekly_uri'] = urljoin(base_uri, 'reports/weekly')

        return resource
