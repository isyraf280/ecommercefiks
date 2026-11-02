from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from app.models import UserAdmin, UserPengguna



def loginView(request):
    if request.user.is_authenticated:
        return redirect('app:index')

    identifier = ''
    if request.method == 'POST':
        identifier = request.POST.get('identifier', '').strip() or request.POST.get('email', '').strip() or request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        if not identifier or not password:
            messages.warning(request, 'Harap isi email/username dan kata sandi Anda.')
            return render(request, 'login.html', {
                'title': 'Login - E-Commerce',
                'heading': 'Masuk ke Akun Anda',
                'identifier': identifier,
            })

        # 1. Coba otentikasi langsung dengan username
        user = authenticate(request, username=identifier, password=password)

        # 2. Jika gagal, cari user berdasarkan email
        if not user:
            users_by_email = User.objects.filter(email__iexact=identifier)
            for cand in users_by_email:
                auth_user = authenticate(request, username=cand.username, password=password)
                if auth_user:
                    user = auth_user
                    break

        if user:
            login(request, user)
            messages.success(request, f'Selamat datang kembali, {user.first_name or user.username}!')
            next_url = request.POST.get('next') or request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('app:dashboard')

        messages.warning(request, 'Email / Username atau password tidak sesuai.')
        return render(request, 'login.html', {
            'title': 'Login - E-Commerce',
            'heading': 'Masuk ke Akun Anda',
            'identifier': identifier,
        })

    return render(request, 'login.html', {
        'title': 'Login - E-Commerce',
        'heading': 'Masuk ke Akun Anda',
        'identifier': identifier,
    })


def registerView(request):
    if request.user.is_authenticated:
        return redirect('app:index')

    name = ''
    email = ''
    if request.method == 'POST':
        name = request.POST.get('first_name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        confirm = request.POST.get('confirm_password', '')

        if not name or not email or not password:
            messages.warning(request, 'Harap isi seluruh formulir pendaftaran.')
        elif len(password) < 6:
            messages.warning(request, 'Kata sandi minimal harus 6 karakter.')
        elif confirm != password:
            messages.warning(request, 'Password dan konfirmasi password tidak cocok.')
        elif User.objects.filter(email=email).exists() or User.objects.filter(username=email).exists():
            messages.warning(request, 'Email sudah terdaftar, silakan gunakan email lain atau langsung login.')
        else:
            new_user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=name,
                last_name='Pengguna',
            )
            UserPengguna.objects.get_or_create(user=new_user, defaults={'telp': ''})
            messages.success(request, 'Registrasi berhasil! Silakan masuk ke akun baru Anda.')
            return redirect('login')

    return render(request, 'register.html', {
        'title': 'Daftar Akun - E-Commerce',
        'heading': 'Pendaftaran Akun Baru',
        'first_name': name,
        'email': email,
    })


@login_required
def LogoutView(request):
    logout(request)
    messages.success(request, 'Anda telah berhasil logout!')
    return redirect('login')   