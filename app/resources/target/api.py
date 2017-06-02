from typing import List
from urllib.parse import urljoin

from flask_sqlalchemy import BaseQuery

from connexion import ProblemException, request

from app import db
from app.libs.resource import ResourceHandler

from app.resources.slo.models import Objective
from app.resources.sli.models import Indicator

from .models import Target


class TargetResource(ResourceHandler):
    model_fields = ('username', 'created', 'updated')

    def get_query(self, slo_id: int, **kwargs) -> BaseQuery:
        return Target.query.filter_by(objective_id=slo_id)

    def validate(self, target: dict, **kwargs) -> None:
        if not target or not target.get('sli_uri'):
            raise ProblemException(title='Invalid target', detail="Target 'sli_uri' must have a value!")

    def new_object(self, target: dict, **kwargs) -> Target:
        fields = self.get_object_fields(target, **kwargs)

        fields['target_from'] = target.get('from', 0.0)
        fields['target_to'] = target.get('to', 0.0)

        product_id = kwargs.get('product_id')
        objective_id = kwargs.get('slo_id')

        target_objective = Objective.query.filter_by(product_id=product_id, id=objective_id).first_or_404()
        fields['objective_id'] = target_objective.id

        indicator_id = self.get_id_from_uri(target['sli_uri'])
        indicator = Indicator.query.filter_by(product_id=product_id, id=indicator_id).first_or_404()
        fields['indicator_id'] = indicator.id

        return Target(**fields)

    def get_objects(self, query: BaseQuery, **kwargs) -> List[Target]:
        return [obj for obj in query.all()]

    def get_object(self, obj_id: int, **kwargs) -> Target:
        return self.get_query(**kwargs).filter_by(id=obj_id).first_or_404()

    def save_object(self, obj: Target, **kwargs) -> Target:
        db.session.add(obj)
        db.session.commit()

        return obj

    def update_object(self, obj: Target, target: dict, **kwargs) -> Target:
        fields = self.get_object_fields(target)

        for field, val in fields.items():
            setattr(obj, field, val)

        obj.target_from = target.get('from', 0.0)
        obj.target_to = target.get('to', 0.0)

        product_id = kwargs.get('product_id')
        objective_id = kwargs.get('slo_id')

        # No need to make extra DB call!
        if obj.objective_id != objective_id:
            target_objective = (
                Objective.query.filter_by(product_id=product_id, id=objective_id).first_or_404()
            )
            obj.objective_id = target_objective.id

        indicator_id = self.get_id_from_uri(target['sli_uri'])
        if obj.indicator_id != indicator_id:
            target_sli = (
                Indicator.query.filter_by(product_id=product_id, id=indicator_id).first_or_404()
            )
            obj.indicator_id = target_sli.id

        db.session.commit()

        return obj

    def delete_object(self, obj: Target, **kwargs) -> None:
        db.session.delete(obj)
        db.session.commit()

    def build_resource(self, obj: Target, **kwargs) -> dict:
        resource = super().build_resource(obj)

        # extra fields
        resource['sli_name'] = obj.indicator.name
        resource['from'] = obj.target_from
        resource['to'] = obj.target_to

        # TODO: get these from the resources as single source of truth?
        product_id = kwargs.get('product_id')
        resource['sli_uri'] = urljoin(request.url_root, 'products/{}/sli/{}'.format(product_id, obj.indicator_id))

        return resource
