from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from functools import wraps


def admin_required(view_func):
    """Apenas usuários is_staff podem acessar."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_staff:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper


def corretor_required(view_func):
    """Qualquer usuário autenticado pode acessar."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper