from flask import request


def extract_span():
    try:
        if hasattr(request, 'current_span'):
            return request.current_span
    except:
        pass

    return None
