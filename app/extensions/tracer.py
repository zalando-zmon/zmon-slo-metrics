import logging

import opentracing

from flask_opentracing import FlaskTracer

from opentracing_utils import init_opentracing_tracer


logger = logging.getLogger(__name__)


# TODO: Compare with using pure opentracing/opentracing-utils and adjust a middleware.

class RequestTracer(FlaskTracer):

    def __init__(self, tracer, trace_all_requests=False, app=None, traced_attributes=[]):
        super().__init__(tracer, trace_all_requests=False, app=None, traced_attributes=None)

    def init_app(self, app, tracer_name=None, traced_attributes=None, **kwargs):
        if tracer:
            init_opentracing_tracer(tracer_name, **kwargs)
            self._tracer = opentracing.tracer

        if traced_attributes is None:
            traced_attributes = []

        @app.before_request
        def start_trace():
            self._before_request_fn(traced_attributes)

        @app.after_request
        def end_trace(response):
            try:
                self._after_request_fn()
            except:
                logger.exception('Failed opentracing response processing!')
            finally:
                return response


tracer = RequestTracer(opentracing.tracer)
