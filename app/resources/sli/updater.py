import math

from typing import Optional

from app import db
from app.libs.zmon import query_sli

from .models import IndicatorValue, Indicator
from .models import insert_indicator_value


MIN_VAL = math.expm1(1e-10)


def update_all_indicators():
    """
    Update all indicators async!
    """
    pass


def update_indicator_values(indicator: Indicator, start: int, end: Optional[int]):
    """Query and update indicator values"""
    session = db.session

    result = query_sli(indicator.name, indicator.source, start, end)

    for minute, val in result.items():
        if val > 0:
            val = max(val, MIN_VAL)
        elif val < 0:
            val = min(val, MIN_VAL * -1)

        iv = IndicatorValue(timestamp=minute, value=val, indicator_id=indicator.id)
        insert_indicator_value(session, iv)

    session.commit()

    return len(result)
