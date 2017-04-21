# from datetime import datetime, timedelta

# from flask_sqlalchemy import BaseQuery

# from connexion import ProblemException
import collections

from sqlalchemy.sql import func, and_

from app.libs.resource import ResourceHandler

from app.resources.slo.models import Objective
from app.resources.target.models import Target
from app.resources.sli.models import Indicator, IndicatorValue


class ReportResource(ResourceHandler):
    @classmethod
    def get(cls, **kwargs) -> dict:
        # resource = cls()

        product_id = kwargs.get('product_id')
        objectives = Objective.query.filter_by(product_id=product_id).all()

        slo = []
        for objective in objectives:
            days = collections.defaultdict(dict)
            q = (
                IndicatorValue.query.
                with_entities(
                    func.max(IndicatorValue.value).label('max'),
                    func.min(IndicatorValue.value).label('min'),
                    func.count(IndicatorValue.value).label('count'),
                    func.avg(IndicatorValue.value).label('avg'),
                    func.date_trunc('day', IndicatorValue.timestamp).label('day'),
                    Indicator.name
                ).
                join(Indicator).
                join(Target,
                     and_(Target.indicator_id == IndicatorValue.indicator_id, Target.objective_id == objective.id)).
                # TODO: Add timestamp conditions (weekly, mongthly, etc..)
                group_by(Indicator.name, 'day')
            )

            for obj in q.all():
                days[obj.day.isoformat()][obj.name] = {
                    'max': obj.max, 'min': obj.min, 'avg': obj.avg, 'count': obj.count
                }

            slo.append(
                {
                    'title': objective.title,
                    'days': days
                }
            )

        return {
            'slo': slo
        }

    def build_resource(self, obj: Indicator, **kwargs) -> dict:
        resource = super().build_resource(obj)

        return resource
