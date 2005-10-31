"""
Decorators for views based on HTTP headers.
"""

from django.utils.decorators import decorator_from_middleware
from django.middleware.http import ConditionalGetMiddleware
from django.utils.httpwrappers import HttpResponseForbidden

conditional_page = decorator_from_middleware(ConditionalGetMiddleware)

def require_http_methods(request_method_list):
    """
    Decorator to make a view only accept particular request methods.  Usage::
    
        @require_http_methods(["GET", "POST"])
        def my_view(request):
            # I can assume now that only GET or POST requests make it this far
            # ...    
            
    Note that request methods ARE case sensitive.
    """
    def decorator(func):
        def inner(request, *args, **kwargs):
            method = request.META.get("REQUEST_METHOD", None) 
            if method not in request_method_list:
                raise HttpResponseForbidden("REQUEST_METHOD '%s' not allowed" % method)
            return func(request, *args, **kwargs)
        return inner
    return decorator

require_GET = require_http_methods(["GET"])
require_GET.__doc__ = "Decorator to require that a view only accept the GET method."

require_POST = require_http_methods(["POST"])
require_POST.__doc__ = "Decorator to require that a view only accept the POST method."