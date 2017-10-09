from flask import request


def extract_span():
    if hasattr(request, 'current_span'):
        return request.current_span
    else:
        return None
