import logging

import opentracing

from flask import request

from opentracing.ext import tags as ot_tags
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

        span = None
        headers_carrier = dict(request.headers.items())

        try:
            span_ctx = opentracing.tracer.extract(opentracing.Format.HTTP_HEADERS, headers_carrier)
            span = opentracing.tracer.start_span(operation_name=operation_name, child_of=span_ctx)
        except (opentracing.InvalidCarrierException, opentracing.SpanContextCorruptedException) as e:
            logger.exception('EXCEPTION')
            span = opentracing.tracer.start_span(operation_name=operation_name, tags={"Extract failed": str(e)})

        if span is None:
            span = opentracing.tracer.start_span(operation_name)

        for attr in request_attr:
            if hasattr(request, attr):
                tag_value = str(getattr(request, attr))
                if tag_value:
                    span.set_tag(attr, tag_value)

        span.set_tag(ot_tags.SPAN_KIND, ot_tags.SPAN_KIND_RPC_SERVER)

        request.current_span = span

    @app.after_request
    def trace_response(response):
        try:
            if hasattr(request, 'current_span'):
                for attr in response_attr:
                    if hasattr(response, attr):
                        request.current_span.set_tag(attr, str(getattr(response, attr)))

                request.current_span.finish()
        finally:
            return response
