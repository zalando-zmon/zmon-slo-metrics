import datetime
import enum
from typing import Dict, Generator, List, Optional, Tuple

import dateutil.parser
import requests

from app.config import LIGHTSTEP_API_KEY, LIGHTSTEP_RESOLUTION_SECONDS

from ..models import Indicator, IndicatorValueLike, PureIndicatorValue
from .base import Source, SourceError


class _Metric(enum.Enum):
    OPS_COUNT = "ops-counts"
    ERRORS_COUNT = "error-counts"
    LATENCY_P50 = "50"
    LATENCY_P75 = "75"
    LATENCY_P90 = "90"
    LATENCY_P99 = "99"

    @classmethod
    def names(cls):
        return [metric.name.lower() for metric in cls]

    @classmethod
    def from_str(cls, metric_str: str) -> "Metric":
        return cls[metric_str.upper().replace("-", "_")]

    def to_request(self) -> Dict:
        if self.name.startswith("LATENCY_"):
            return {"percentile": self.value}

        return {f"include-{self.value}": 1}

    def get_datapoints(self, response) -> Generator[Tuple[str, str], None, None]:
        attributes = response["data"]["attributes"]

        if self.name.startswith("LATENCY_"):
            for latency in attributes["latencies"]:
                if latency["percentile"] == self.value:
                    values = latency["latency-ms"]
                    break
            else:
                raise SourceError(
                    f"No latencies found for {self.value}th percentile in timeseries."
                )
        else:
            values = attributes[self.value]

        return (
            (window["youngest-time"], value)
            for window, value in zip(attributes["time-windows"], values)
        )


def _paginate_timerange(
    from_: datetime.datetime,
    to: datetime.datetime,
    page: Optional[int] = None,
    per_page: Optional[int] = None,
) -> Tuple[datetime.datetime, datetime.datetime]:
    delta_seconds = (to - from_).total_seconds()
    values_count = delta_seconds / LIGHTSTEP_RESOLUTION_SECONDS
    from_ = from_ + datetime.timedelta(
        seconds=(page - 1) * per_page * LIGHTSTEP_RESOLUTION_SECONDS
    )
    to = from_ + datetime.timedelta(seconds=LIGHTSTEP_RESOLUTION_SECONDS * per_page)

    return from_, to


class Lightstep(Source):
    @classmethod
    def validate_config(cls, config: Dict):
        stream_id = config.get("stream_id")
        metric = config.get("metric")

        if not stream_id:
            raise SourceError(
                "LightStep stream ID is required, but was not provided or is empty. "
                "Please provide a valid LightStep stream ID in the 'stream_id' property of the source configuration."
            )
        try:
            _Metric.from_str(metric)
        except:  # noqa
            raise SourceError(
                "Metric name for the LightStep source is not correct. "
                "Please provide a valid metric name in the 'metric' property of the source configuration. "
                f"Current value is {metric!r} whereas the valid choices are: {', '.join(_Metric.names())}. "
            )

    def __init__(self, indicator: Indicator, stream_id: str, metric: str):
        self.indicator = indicator
        self.stream_id = stream_id
        self.metric = _Metric.from_str(metric)

    def get_indicator_values(
        self,
        from_: datetime.datetime,
        to: datetime.datetime,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
    ) -> Tuple[List[IndicatorValueLike], None]:
        if page and per_page:
            from_, to = _paginate_timerange(from_, to, page, per_page)

        params = {
            "oldest-time": from_.replace(tzinfo=datetime.timezone.utc).isoformat(),
            "youngest-time": to.replace(tzinfo=datetime.timezone.utc).isoformat(),
            "resolution-ms": str(LIGHTSTEP_RESOLUTION_SECONDS * 1000),
            **self.metric.to_request(),
        }
        response = requests.get(
            url=f"https://api.lightstep.com/public/v0.1/Zalando/projects/Production/searches/{self.stream_id}/timeseries",
            headers={"Authorization": f"Bearer {LIGHTSTEP_API_KEY}"},
            params=params,
        )
        if response.status_code == 401:
            raise SourceError(
                "Given Lightstep API key is probably wrong. Please verify if the LIGHTSTEP_API_KEY environment variable contains a valid key."
            )
        response = response.json()
        errors = response.get("errors")
        if errors:
            raise SourceError(
                f"Something went wrong with a request to the Lightstep API: {errors}."
            )

        return (
            [
                PureIndicatorValue(
                    dateutil.parser.parse(timestamp_str, ignoretz=True), value
                )
                for timestamp_str, value in self.metric.get_datapoints(response)
            ],
            None,
        )

    def update_indicator_values(self, *_, **__) -> int:
        return 0
