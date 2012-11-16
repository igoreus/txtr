from django.http import HttpResponseRedirect

def anonymous_required(redirect_url=None):
    """
    Decorator for views that checks that the user is anonymous
    """
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            if request.user.is_anonymous():
                result = func(request, *args, **kwargs)
            else:
                result = HttpResponseRedirect(redirect_url if redirect_url else '/')
            return result
        return wrapper
    return decorator