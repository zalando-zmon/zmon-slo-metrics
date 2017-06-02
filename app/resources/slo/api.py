from typing import List
from urllib.parse import urljoin

from flask_sqlalchemy import BaseQuery

from connexion import ProblemException, request

from app import db
from app.libs.resource import ResourceHandler, READ_ONLY_FIELDS

from app.resources.product.models import Product

from .models import Objective


class SLOResource(ResourceHandler):
    model_fields = ('title', 'description', 'username', 'created', 'updated')

    def get_query(self, product_id: int, **kwargs) -> BaseQuery:
        return Objective.query.filter_by(product_id=product_id)

    def validate(self, slo: dict, **kwargs) -> None:
        if not slo or not slo.get('title'):
            raise ProblemException(title='Invalid SLO', detail="SLO 'title' must have a value!")

    def new_object(self, slo: dict, **kwargs) -> Objective:
        fields = {}

        for field in self.model_fields:
            if field in READ_ONLY_FIELDS:
                continue
            fields[field] = slo.get(field)

        product_id = kwargs.get('product_id')

        slo_product = Product.query.get_or_404(product_id)

        fields['product_id'] = slo_product.id

        return Objective(**fields)

    def get_objects(self, query: BaseQuery, **kwargs) -> List[Objective]:
        return [obj for obj in query.all()]

    def get_object(self, obj_id: int, **kwargs) -> Objective:
        return self.get_query(**kwargs).filter_by(id=obj_id).first_or_404()

    def save_object(self, obj: Objective, **kwargs) -> Objective:
        db.session.add(obj)
        db.session.commit()

        return obj

    def update_object(self, obj: Objective, slo: dict, **kwargs) -> Objective:
        fields = self.get_object_fields(slo)

        for field, val in fields.items():
            setattr(obj, field, val)

        product_id = kwargs.get('product_id')

        # No need to make extra DB call!
        if obj.product_id != product_id:
            slo_product = Product.query.get_or_404(product_id)
            obj.product_id = slo_product.id

        db.session.commit()

        return obj

    def delete_object(self, obj: Objective, **kwargs) -> None:
        db.session.delete(obj)
        db.session.commit()

    def build_resource(self, obj: Objective, **kwargs) -> dict:
        resource = super().build_resource(obj)

        # extra fields
        resource['product_name'] = obj.product.name

        # Links
        base_uri = resource['uri'] + '/'

        # TODO: get from corresponding build_resource()
        resource['targets'] = [urljoin(base_uri, 'targets/{}'.format(t.id)) for t in obj.targets]

        # TODO: get these from the resources as single source of truth?
        resource['product_uri'] = urljoin(request.url_root, 'products/{}'.format(obj.product_id))
        resource['slo_targets_uri'] = urljoin(base_uri, 'targets')

        return resource
