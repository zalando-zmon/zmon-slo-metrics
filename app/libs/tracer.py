from flask import request

from app.extensions import tracer


def extract_span():
    try:
        return tracer.get_span(request)
    except:
        return None
