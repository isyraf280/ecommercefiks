from django.shortcuts import render, redirect

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.utils import timezone
from .models import UserAdmin, UserPengguna, Provinsi, Produk, KategoriProduk, Pesanan


@login_required
def index(request):
    today = timezone.localdate()
    if request.user.last_name == 'Super Admin' or request.user.is_superuser or request.user.is_staff:
        userC = UserAdmin.objects.filter(username=request.user).first()
        total_pengguna = UserPengguna.objects.count()
        total_provinsi = Provinsi.objects.count()
        total_produk = Produk.objects.count()
        total_kategori = KategoriProduk.objects.count()
        total_pesanan = Pesanan.objects.count()

        pesanan_selesai = Pesanan.objects.filter(status__in=['dibayar', 'diproses', 'dikirim', 'selesai'])
        total_revenue = sum(p.grand_total for p in pesanan_selesai)

        recent_orders = Pesanan.objects.all().order_by('-waktu_pesan')[:8]
        recent_products = Produk.objects.select_related('kategori').all()[:6]
        recent_customers = UserPengguna.objects.select_related('user').all()[:6]

        context = {
            'title': 'Lesaffrone Workspace — Admin Panel',
            'heading': 'Dashboard Administrator',
            'photo': userC.photo if userC and userC.photo else None,
            'userdetail': userC if userC else None,
            'total_pengguna': total_pengguna,
            'total_provinsi': total_provinsi,
            'total_produk': total_produk,
            'total_kategori': total_kategori,
            'total_pesanan': total_pesanan,
            'total_revenue': total_revenue,
            'recent_orders': recent_orders,
            'recent_products': recent_products,
            'recent_customers': recent_customers,
            'today': today,
        }
        return render(request, 'admin_super/index.html', context)

    elif request.user.last_name == 'Pengguna':
        userC = UserPengguna.objects.filter(user=request.user).first()
        buyer_orders = Pesanan.objects.filter(user=request.user).order_by('-waktu_pesan')
        total_orders = buyer_orders.count()

        context = {
            'title': 'Your Bakery Moments — Lesaffrone',
            'heading': 'Dashboard Pelanggan',
            'photo': userC.photo if userC and userC.photo else None,
            'userdetail': userC,
            'today': today,
            'buyer_orders': buyer_orders,
            'total_orders': total_orders,
            'reward_points': total_orders * 80,
        }
        return render(request, 'pengguna/index.html', context)

    else:
        # Fallback jika role belum terdefinisi secara spesifik
        userC = UserPengguna.objects.filter(user=request.user).first()
        buyer_orders = Pesanan.objects.filter(user=request.user).order_by('-waktu_pesan')
        total_orders = buyer_orders.count()

        context = {
            'title': 'Your Bakery Moments — Lesaffrone',
            'heading': 'Dashboard Pelanggan',
            'photo': userC.photo if userC and userC.photo else None,
            'userdetail': userC,
            'today': today,
            'buyer_orders': buyer_orders,
            'total_orders': total_orders,
            'reward_points': total_orders * 80,
        }
        return render(request, 'pengguna/index.html', context)
