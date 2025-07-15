from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from functools import wraps

def role_required(allowed_roles):
    """
    Decorator for views that checks if the user has one of the specified roles.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            user_profile = request.user.userprofile
            if not user_profile.role:
                raise PermissionDenied
                
            if user_profile.role.name in allowed_roles:
                return view_func(request, *args, **kwargs)
            raise PermissionDenied
        return wrapper
    return decorator