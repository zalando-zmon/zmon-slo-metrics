from typing import List

from flask_sqlalchemy import BaseQuery, Pagination

from connexion import ProblemException

from app import db
from app.libs.resource import ResourceHandler
from app.utils import slugger

from .models import ProductGroup


class ProductGroupResource(ResourceHandler):
    model_fields = ('name', 'department', 'username', 'created', 'updated')

    def get_filter_kwargs(self, **kwargs) -> dict:
        """Return relevant filters"""
        filters = {}

        if 'name' in kwargs:
            filters['name'] = kwargs['name']

        return filters

    def get_query(self, **kwargs) -> BaseQuery:
        return ProductGroup.query

    def validate(self, product_group: dict, **kwargs) -> None:
        if not product_group or not product_group.get('name'):
            raise ProblemException(title='Invalid product group', detail='Product group name must have a value!')

    def new_object(self, product_group: dict, **kwargs) -> ProductGroup:
        return ProductGroup(**product_group)

    def get_objects(self, query: Pagination, **kwargs) -> List[ProductGroup]:
        return [obj for obj in query.items]

    def get_object(self, obj_id: int, **kwargs) -> ProductGroup:
        return ProductGroup.query.get_or_404(obj_id)

    def save_object(self, obj: ProductGroup, **kwargs) -> ProductGroup:
        db.session.add(obj)
        db.session.commit()

        return obj

    def update_object(self, obj: ProductGroup, product_group: dict, **kwargs) -> ProductGroup:
        obj.name = product_group.get('name')
        obj.department = product_group.get('department', '')

        db.session.commit()

        return obj

    def delete_object(self, obj: ProductGroup, **kwargs) -> None:
        if obj.products.count():
            raise ProblemException(
                status=403, title='Deleting Product group forbidden',
                detail='Some products still belong to this product group.')

        db.session.delete(obj)
        db.session.commit()

    def build_resource(self, obj, **kwargs) -> dict:
        resource = super().build_resource(obj)

        # extra fields
        resource['slug'] = slugger(obj.name)

        return resource
