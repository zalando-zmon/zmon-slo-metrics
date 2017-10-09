import logging

import opentracing

from flask import request
from flask_opentracing import FlaskTracer

from opentracing_utils import init_opentracing_tracer


logger = logging.getLogger(__name__)


DEFUALT_REQUEST_ATTRIBUTES = ('url', 'method')
DEFUALT_RESPONSE_ATTRIBUTES = ('status_code',)


# TODO: Compare with using pure opentracing/opentracing-utils and adjust a middleware.

def trace_flask(app, tracer_name=None, before_request=None, after_request=None,
                request_attr=DEFUALT_REQUEST_ATTRIBUTES, response_attr=DEFUALT_RESPONSE_ATTRIBUTES, **kwargs):

    logger.info('Initializing opentracing tracer: {}'.format(tracer_name))

    init_opentracing_tracer(tracer_name, **kwargs)

    @app.before_request
    def trace_request():
        operation_name = request.endpoint

        # headers = {}
        # for k, v in request.headers:
        #     headers[k.lower()] = v

        span = None

        try:
            span_ctx = opentracing.tracer.extract(opentracing.Format.HTTP_HEADERS, request.headers)
            span = opentracing.tracer.start_span(operation_name=operation_name, child_of=span_ctx)
        except (opentracing.InvalidCarrierException, opentracing.SpanContextCorruptedException) as e:
            span = opentracing.tracer.start_span(operation_name=operation_name, tags={"Extract failed": str(e)})

        if span is None:
            span = opentracing.tracer.start_span(operation_name)

        for attr in request_attr:
            if hasattr(request, attr):
                payload = str(getattr(request, attr))
                if payload:
                    span.set_tag(attr, payload)

        request.current_span = span

    @app.after_request
    def trace_response(response):
        try:
            if hasattr(request, 'current_span'):
                for attr in response_attr:
                    if hasattr(response, attr):
                        print(response.status_code)
                        request.current_span.set_tag(attr, str(getattr(response, attr)))

                request.current_span.finish()
        finally:
            return response


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
