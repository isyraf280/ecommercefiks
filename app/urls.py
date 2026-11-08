from django.urls import path

from . import views
from . import views_admin
from . import views_pengguna
from . import views_katalog
from . import views_payment


urlpatterns = [
    ###### ADMIN KEANGGOTAAN INDIVIDU ######   
    path('profile/admin', views_admin.profile_admin, name='profile_admin'),

    ###### PENGUNA/CLIENTS #######
    path('profile/pengguna', views_pengguna.profile_pengguna, name='profile_pengguna'),

    ###### UMUM ######         
    path('dashboard', views.index, name='dashboard'),
    path('', views.index, name='index'),

    ###### ADMIN KATALOG PRODUK ######
    path('admin/katalog/', views_katalog.admin_katalog, name='admin_katalog'),
    path('admin/katalog/tambah/', views_katalog.admin_tambah_produk, name='admin_tambah_produk'),
    path('admin/katalog/edit/<slug:slug>/', views_katalog.admin_edit_produk, name='admin_edit_produk'),
    path('admin/katalog/hapus/<slug:slug>/', views_katalog.admin_hapus_produk, name='admin_hapus_produk'),

    path('admin/kategori/', views_katalog.admin_kategori, name='admin_kategori'),
    path('admin/kategori/tambah/', views_katalog.admin_tambah_kategori, name='admin_tambah_kategori'),
    path('admin/kategori/edit/<uuid:pk>/', views_katalog.admin_edit_kategori, name='admin_edit_kategori'),
    path('admin/kategori/hapus/<uuid:pk>/', views_katalog.admin_hapus_kategori, name='admin_hapus_kategori'),

    ###### ADMIN PESANAN & GATEWAY ######
    path('admin/pesanan/', views_payment.admin_daftar_pesanan, name='admin_pesanan'),
    path('admin/pesanan/<uuid:order_id>/update-status/', views_payment.admin_update_status_pesanan, name='admin_update_status_pesanan'),

    ###### PENGGUNA: KATALOG ######
    path('katalog/', views_katalog.katalog_pengguna, name='katalog_pengguna'),
    path('katalog/<slug:slug>/', views_katalog.detail_produk, name='detail_produk'),
    path('seed-katalog/', views_katalog.seed_katalog_view, name='seed_katalog'),
]
