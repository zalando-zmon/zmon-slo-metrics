import collections

from datetime import datetime
from dateutil.relativedelta import relativedelta

from connexion import ProblemException

from sqlalchemy.sql import text

from app import db
from app.libs.resource import ResourceHandler

from app.resources.product.models import Product
# from app.resources.slo.models import Objective
from app.resources.sli.models import Indicator


REPORT_TYPES = ('weekly', 'monthly', 'quarterly')


class ReportResource(ResourceHandler):
    @classmethod
    def get(cls, **kwargs) -> dict:
        report_type = kwargs.get('report_type')
        if report_type not in REPORT_TYPES:
            raise ProblemException(
                status=404, title='Resource not found',
                detail='Report type ({}) is invalid. Supported types are: {}'.format(report_type, REPORT_TYPES))

        product_id = kwargs.get('product_id')
        product = Product.query.get_or_404(product_id)

        objectives = product.objectives.all()

        now = datetime.utcnow()
        start = now - relativedelta(days=7)

        if report_type != 'weekly':
            months = 1 if report_type == 'monthly' else 3
            start = now - relativedelta(months=months)

        unit = 'day' if report_type == 'weekly' else 'week'

        slo = []
        for objective in objectives:
            days = collections.defaultdict(dict)

            q = text('''
                SELECT
                    date_trunc(:unit, indicatorvalue.timestamp) AS day,
                    indicator.name AS name,
                    MIN(indicatorvalue.value) AS min,
                    AVG(indicatorvalue.value) AS avg,
                    MAX(indicatorvalue.value) AS max,
                    COUNT(indicatorvalue.value) AS count,
                    (SELECT SUM(CASE b WHEN TRUE THEN 0 ELSE 1 END) FROM UNNEST(array_agg(indicatorvalue.value BETWEEN
                        COALESCE(target.target_from, :lower) AND COALESCE(target.target_to, :upper))) AS dt(b)
                    ) AS breaches
                FROM indicatorvalue
                JOIN target ON target.indicator_id = indicatorvalue.indicator_id AND target.objective_id = :objective_id
                JOIN indicator ON indicator.id = indicatorvalue.indicator_id
                WHERE indicatorvalue.timestamp >= :start AND indicatorvalue.timestamp < :now
                GROUP BY day, name
                ''')  # noqa

            params = {
                'unit': unit, 'objective_id': objective.id, 'start': start, 'now': now, 'lower': float('-inf'),
                'upper': float('inf')
            }
            for obj in db.session.execute(q, params):
                days[obj.day.isoformat()][obj.name] = {
                    'max': obj.max, 'min': obj.min, 'avg': obj.avg, 'count': obj.count, 'breaches': obj.breaches
                }

            slo.append(
                {
                    'title': objective.title,
                    'targets': [
                        {
                            'from': t.target_from, 'to': t.target_to, 'sli_name': t.indicator.name,
                            'unit': t.indicator.unit
                        }
                        for t in objective.targets
                    ],
                    'days': days
                }
            )

        return {
            'product_name': product.name,
            'product_group_name': product.product_group.name,
            'department': product.product_group.department,
            'slo': slo,
        }

    def build_resource(self, obj: Indicator, **kwargs) -> dict:
        resource = super().build_resource(obj)

        return resource
