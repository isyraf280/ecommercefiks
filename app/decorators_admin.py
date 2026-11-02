from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from .models import UserAdmin, UserPengguna


def check_useradmin(function):
    def wrapper(request, *args, **kwargs):   
        useradmin = UserAdmin.objects.filter(username=request.user).first()
        request.useradmin = useradmin
        if not useradmin or useradmin.photo == None:
            messages.error(request, "Lengkapi data Anda terlebih dahulu!")
            return redirect('app:profile_admin')               
        return function(request, *args, **kwargs)
    return wrapper


def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        # Pengecekan superuser atau Super Admin
        if request.user.is_superuser or request.user.last_name == "Super Admin":
            return view_func(request, *args, **kwargs)
        else:
            return redirect('app:dashboard')
    return _wrapped_view


def check_userpengguna(function):
    def wrapper(request, *args, **kwargs):
        userpengguna = UserPengguna.objects.filter(user=request.user).first()
        request.userpengguna = userpengguna
        if not userpengguna or userpengguna.photo == None or userpengguna.gender == None:
            messages.error(request, "Lengkapi data Anda terlebih dahulu!")
            return redirect('app:profile_pengguna')               
        return function(request, *args, **kwargs)
    return wrapper


def pengguna_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.last_name != "Pengguna":
            return redirect('app:dashboard')
            
        return view_func(request, *args, **kwargs)
    return _wrapped_view