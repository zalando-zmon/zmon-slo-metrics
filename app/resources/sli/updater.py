import os
import math
import logging
import warnings

from flask import Flask

from datetime import datetime, timedelta
from typing import Optional

from gevent.pool import Pool

from opentracing_utils import trace, get_span_from_kwargs

from app.config import MAX_QUERY_TIME_SLICE, UPDATER_CONCURRENCY
from app.extensions import db
from app.libs.zmon import query_sli
from app.libs.tracer import extract_span

from .models import IndicatorValue, Indicator
from .models import insert_indicator_value


MIN_VAL = math.expm1(1e-10)

logger = logging.getLogger(__name__)

updater_pool = Pool(UPDATER_CONCURRENCY)


@trace(pass_span=True)
def update_all_indicators(app: Flask, **kwargs):
    """
    Update all indicators async!
    """
    if os.environ.get('SLR_LOCAL_ENV'):
        warnings.warn('Running on local env while not setting up gevent properly!')

    _, current_span = get_span_from_kwargs(**kwargs)

    for indicator in Indicator.query.all():
        try:
            updater_pool.spawn(update_indicator, app, indicator, parent_span=current_span)
        except:
            logger.exception('Updater: Failed to spawn indicator updater!')

    updater_pool.join()


@trace(pass_span=True)
def update_indicator(app: Flask, indicator: Indicator, **kwargs):
    logger.info('Updater: Updating Indicator {} values for product {}'.format(indicator.name, indicator.product.name))

    _, current_span = get_span_from_kwargs(**kwargs)

    with app.app_context():
        now = datetime.utcnow()
        newest_dt = now - timedelta(minutes=MAX_QUERY_TIME_SLICE)

        try:
            newest_iv = (
                IndicatorValue.query.
                with_entities(db.func.max(IndicatorValue.timestamp).label('timestamp')).
                filter(IndicatorValue.timestamp >= newest_dt,
                       IndicatorValue.timestamp < now,
                       IndicatorValue.indicator_id == indicator.id).
                first()
            )

            if newest_iv and newest_iv.timestamp:
                start = (now - newest_iv.timestamp).seconds // 60 + 5  # add some overlapping
            else:
                start = MAX_QUERY_TIME_SLICE

            count = update_indicator_values(indicator, start=start, parent_span=current_span)
            logger.info('Updater: Updated {} indicator values "{}" for product "{}"'.format(
                count, indicator.name, indicator.product.name))
        except:
            logger.exception('Updater: Failed to update indicator "{}" values for product "{}"'.format(
                indicator.name, indicator.product.name))


@trace(span_extractor=extract_span, pass_span=True)
def update_indicator_values(indicator: Indicator, start: int, end: Optional[int]=None, **kwargs):
    """Query and update indicator values"""
    session = db.session

    _, current_span = get_span_from_kwargs(**kwargs)

    result = query_sli(indicator.name, indicator.source, start, end, parent_span=current_span)

    for minute, val in result.items():
        if val > 0:
            val = max(val, MIN_VAL)
        elif val < 0:
            val = min(val, MIN_VAL * -1)

        iv = IndicatorValue(timestamp=minute, value=val, indicator_id=indicator.id)
        insert_indicator_value(session, iv)

    session.commit()

    return len(result)
