import collections

from app.db import dbconn
from app.handler.slo import get as get_service_level_objectives
from app.utils import strip_column_prefix


def get_service_level_objective_report(product, report_type):
    with dbconn() as conn:
        cur = conn.cursor()
        cur.execute('''SELECT p.*, pg_name AS pg_product_group_name, pg_slug AS pg_product_group_slug, pg_department
                FROM zsm_data.product p
                JOIN zsm_data.product_group ON pg_id = p_product_group_id
                WHERE p_slug = %s''', (product,))
        row = cur.fetchone()

        if not row:
            return 'Product not found', 404

        product_data = strip_column_prefix(row._asdict())
        service_level_objectives = get_service_level_objectives(product)

        for slo in service_level_objectives:
            days = collections.defaultdict(dict)
            cur.execute(
                '''
                SELECT
                    date_trunc(\'day\', sli_timestamp) AS day,
                    sli_name AS name,
                    ds_definition #>> ARRAY['aggregation', 'type'] AS aggregate_type,
                    MIN(sli_value) AS min,
                    AVG(sli_value),
                    MAX(sli_value),
                    COUNT(sli_value),
                    (SELECT SUM(CASE b WHEN TRUE THEN 0 ELSE 1 END) FROM UNNEST(array_agg(sli_value BETWEEN
                        COALESCE(slit_from, \'-Infinity\') AND COALESCE(slit_to, \'Infinity\'))) AS dt(b)
                    ) AS agg
                FROM zsm_data.service_level_indicator
                JOIN zsm_data.service_level_indicator_target ON slit_sli_name = sli_name
                JOIN zsm_data.service_level_objective ON slo_id = slit_slo_id AND slo_id = %s
                JOIN zsm_data.product ON p_id = slo_product_id AND p_slug = %s
                JOIN zsm_data.data_source ON ds_product_id = p_id AND ds_sli_name = sli_name
                WHERE
                    sli_timestamp >= date_trunc(\'day\', \'now\'::TIMESTAMP - INTERVAL \'7 days\') AND
                    sli_product_id = %s
                GROUP BY date_trunc(\'day\', sli_timestamp), sli_name, ds_definition #>> ARRAY['aggregation', 'type']
                ''',
                (slo['id'], product, product_data['id'],))

            rows = cur.fetchall()
            for row in rows:
                days[row.day.isoformat()][row.name] = {'min': row.min, 
                                                       'avg': row.avg, 
                                                       'max': row.max,
                                                       'count': row.count, 
                                                       'breaches': row.agg,
                                                       'aggregate_type': row.aggregate_type}
            slo['days'] = days

    return {'product': product_data, 'service_level_objectives': service_level_objectives}
