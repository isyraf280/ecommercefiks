from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from . import views
from app import views_katalog
from app import views_payment

urlpatterns = [
    path('admin/', admin.site.urls),
]

urlpatterns += [
    path('', views_katalog.landing_page, name='home'),
    path('katalog/', views_katalog.katalog_pengguna, name='katalog'),
    path('katalog/<slug:slug>/', views_katalog.detail_produk, name='detail_produk'),
    path('seed-katalog/', views_katalog.seed_katalog_view, name='seed_katalog'),

    # ── KERANJANG & CHECKOUT ──
    path('keranjang/', views_payment.lihat_keranjang, name='lihat_keranjang'),
    path('keranjang/tambah/<slug:slug>/', views_payment.tambah_keranjang, name='tambah_keranjang'),
    path('keranjang/kurangi/<slug:slug>/', views_payment.kurangi_keranjang, name='kurangi_keranjang'),
    path('keranjang/hapus/<slug:slug>/', views_payment.hapus_keranjang, name='hapus_keranjang'),
    path('beli-sekarang/<slug:slug>/', views_payment.beli_sekarang, name='beli_sekarang'),
    path('checkout/', views_payment.checkout_view, name='checkout'),

    # ── SANDBOX PAYMENT GATEWAY ──
    path('payment/sandbox/<uuid:order_id>/', views_payment.payment_sandbox_view, name='payment_sandbox'),
    path('payment/sandbox/<uuid:order_id>/action/<str:action>/', views_payment.payment_simulate_action, name='payment_simulate_action'),
    path('pesanan/invoice/<uuid:order_id>/', views_payment.order_invoice_view, name='order_invoice'),
    path('pesanan/riwayat/', views_payment.riwayat_pesanan_view, name='riwayat_pesanan'),

    path('login/', views.loginView, name='login'),
    path('register/', views.registerView, name='register'),
    path('logout/', views.LogoutView, name='logout'),
    path('app/', include(('app.urls', 'app'), namespace='app')),
]

urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)