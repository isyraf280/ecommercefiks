import uuid
import random
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from app.decorators_admin import admin_required
from .models import Produk, Pesanan, ItemPesanan, TransaksiPaymentGateway


# ─────────────────────────────────────────────────────────────
#  HELPER KERANJANG (SESSION-BASED CART)
# ─────────────────────────────────────────────────────────────

def _get_cart(request):
    """Mengambil keranjang dari session request."""
    if 'cart' not in request.session:
        request.session['cart'] = {}
    return request.session['cart']


def _save_cart(request, cart):
    """Menyimpan keranjang ke session."""
    request.session['cart'] = cart
    request.session.modified = True


# ─────────────────────────────────────────────────────────────
#  KERANJANG BELANJA
# ─────────────────────────────────────────────────────────────

def tambah_keranjang(request, slug):
    """Menambahkan produk ke keranjang belanja."""
    produk = get_object_or_404(Produk, slug=slug, tersedia=True)
    cart = _get_cart(request)
    p_id = str(produk.id)

    jumlah_tambah = int(request.POST.get('jumlah', 1))
    if jumlah_tambah < 1:
        jumlah_tambah = 1

    if p_id in cart:
        cart[p_id]['jumlah'] += jumlah_tambah
    else:
        cart[p_id] = {
            'nama': produk.nama_produk,
            'slug': produk.slug,
            'harga': float(produk.harga),
            'jumlah': jumlah_tambah,
            'satuan': produk.satuan,
            'foto': produk.foto.url if produk.foto else '',
        }

    _save_cart(request, cart)
    messages.success(request, f'"{produk.nama_produk}" ({jumlah_tambah} {produk.satuan}) ditambahkan ke keranjang!')

    next_url = request.POST.get('next') or request.GET.get('next')
    if next_url:
        return redirect(next_url)
    return redirect('lihat_keranjang')


def beli_sekarang(request, slug):
    """Fitur Beli Sekarang: langsung masukkan ke keranjang dan arahkan ke checkout."""
    produk = get_object_or_404(Produk, slug=slug, tersedia=True)
    cart = _get_cart(request)
    p_id = str(produk.id)

    # Tambahkan atau timpa 1 item
    if p_id in cart:
        cart[p_id]['jumlah'] += 1
    else:
        cart[p_id] = {
            'nama': produk.nama_produk,
            'slug': produk.slug,
            'harga': float(produk.harga),
            'jumlah': 1,
            'satuan': produk.satuan,
            'foto': produk.foto.url if produk.foto else '',
        }
    _save_cart(request, cart)
    return redirect('checkout')


def kurangi_keranjang(request, slug):
    """Mengurangi 1 jumlah item di keranjang."""
    produk = get_object_or_404(Produk, slug=slug)
    cart = _get_cart(request)
    p_id = str(produk.id)

    if p_id in cart:
        cart[p_id]['jumlah'] -= 1
        if cart[p_id]['jumlah'] <= 0:
            del cart[p_id]
        _save_cart(request, cart)

    return redirect('lihat_keranjang')


def hapus_keranjang(request, slug):
    """Menghapus produk dari keranjang."""
    produk = get_object_or_404(Produk, slug=slug)
    cart = _get_cart(request)
    p_id = str(produk.id)

    if p_id in cart:
        del cart[p_id]
        _save_cart(request, cart)
        messages.info(request, f'"{produk.nama_produk}" telah dihapus dari keranjang.')

    return redirect('lihat_keranjang')


def lihat_keranjang(request):
    """Halaman tampilan daftar item di keranjang."""
    cart = _get_cart(request)
    cart_items = []
    total_harga = Decimal('0')

    for p_id, item in cart.items():
        subtotal = Decimal(str(item['harga'])) * int(item['jumlah'])
        total_harga += subtotal
        cart_items.append({
            'id': p_id,
            'nama': item['nama'],
            'slug': item['slug'],
            'harga': Decimal(str(item['harga'])),
            'jumlah': item['jumlah'],
            'satuan': item['satuan'],
            'foto': item.get('foto', ''),
            'subtotal': subtotal,
        })

    # Ongkir gratis jika belanja > Rp 100.000
    ongkir = Decimal('0') if total_harga >= Decimal('100000') or total_harga == 0 else Decimal('10000')
    grand_total = total_harga + ongkir

    context = {
        'title': 'Keranjang Belanja - Lesaffrone Bakery',
        'heading': 'Keranjang Belanja Anda',
        'cart_items': cart_items,
        'total_harga': total_harga,
        'ongkir': ongkir,
        'grand_total': grand_total,
        'is_empty': len(cart_items) == 0,
    }
    return render(request, 'pembayaran/keranjang.html', context)


# ─────────────────────────────────────────────────────────────
#  CHECKOUT PESANAN
# ─────────────────────────────────────────────────────────────

def checkout_view(request):
    """Halaman checkout dan formulir data pengiriman."""
    cart = _get_cart(request)
    if not cart:
        messages.warning(request, 'Keranjang belanja Anda masih kosong. Silakan pilih produk terlebih dahulu.')
        return redirect('katalog')

    cart_items = []
    total_harga = Decimal('0')

    for p_id, item in cart.items():
        subtotal = Decimal(str(item['harga'])) * int(item['jumlah'])
        total_harga += subtotal
        cart_items.append({
            'id': p_id,
            'nama': item['nama'],
            'slug': item['slug'],
            'harga': Decimal(str(item['harga'])),
            'jumlah': item['jumlah'],
            'satuan': item['satuan'],
            'foto': item.get('foto', ''),
            'subtotal': subtotal,
        })

    ongkir = Decimal('0') if total_harga >= Decimal('100000') else Decimal('10000')
    grand_total = total_harga + ongkir

    if request.method == 'POST':
        nama = request.POST.get('nama_pelanggan', '').strip()
        telepon = request.POST.get('telepon', '').strip()
        email = request.POST.get('email', '').strip()
        alamat = request.POST.get('alamat_pengiriman', '').strip()
        catatan = request.POST.get('catatan', '').strip()
        metode = request.POST.get('metode_pembayaran', 'qris')

        if not nama or not telepon or not alamat:
            messages.error(request, 'Harap lengkapi nama penerima, nomor telepon/WhatsApp, dan alamat pengiriman.')
        else:
            # Generate invoice number
            now_str = timezone.now().strftime('%Y%m%d')
            rand_code = ''.join(random.choices('ABCDEFGHJKLMNPQRSTUVWXYZ23456789', k=4))
            nomor_pesanan = f"ORD-{now_str}-{rand_code}"

            pesanan = Pesanan.objects.create(
                nomor_pesanan=nomor_pesanan,
                user=request.user if request.user.is_authenticated else None,
                nama_pelanggan=nama,
                email=email,
                telepon=telepon,
                alamat_pengiriman=alamat,
                catatan=catatan,
                total_harga=total_harga,
                ongkir=ongkir,
                grand_total=grand_total,
                status='menunggu_pembayaran',
                metode_pembayaran=metode,
            )

            # Buat ItemPesanan
            for item in cart_items:
                prod = Produk.objects.filter(slug=item['slug']).first()
                ItemPesanan.objects.create(
                    pesanan=pesanan,
                    produk=prod,
                    nama_produk=item['nama'],
                    harga_satuan=item['harga'],
                    jumlah=item['jumlah'],
                    subtotal=item['subtotal'],
                )

            # Inisialisasi Transaksi Payment Gateway Sandbox
            trx_id = f"TRX-SBX-{now_str}-{random.randint(100000, 999999)}"
            bank_code = ''
            va_number = ''

            if metode == 'va_bca':
                bank_code = 'BCA'
                va_number = f"88012{random.randint(10000000, 99999999)}"
            elif metode == 'va_mandiri':
                bank_code = 'MANDIRI'
                va_number = f"89012{random.randint(10000000, 99999999)}"
            elif metode == 'va_bri':
                bank_code = 'BRI'
                va_number = f"88712{random.randint(10000000, 99999999)}"

            qr_data = f"00020101021226680016ID.CO.LESAFFRONE011893600998877665544352045812530336054{grand_total:.0f}5802ID5910LESAFFRONE6007JAKARTA6304"

            TransaksiPaymentGateway.objects.create(
                pesanan=pesanan,
                transaction_id=trx_id,
                merchant_id='LESAFFRONE-SANDBOX',
                payment_type=metode,
                bank=bank_code,
                va_number=va_number,
                qr_string=qr_data,
                status_transaksi='pending',
                status_code='201',
                status_message='Menunggu pembayaran pelanggan pada sandbox gateway',
                expired_at=timezone.now() + timezone.timedelta(hours=24),
            )

            # Kosongkan keranjang setelah order dibuat
            request.session['cart'] = {}
            request.session.modified = True

            return redirect('payment_sandbox', order_id=pesanan.id)

    # Pre-fill user data jika sudah login
    initial_nama = ''
    initial_telp = ''
    initial_email = ''
    initial_alamat = ''
    if request.user.is_authenticated:
        initial_nama = request.user.first_name or request.user.username
        initial_email = request.user.email
        if hasattr(request.user, 'anggota'):
            initial_telp = request.user.anggota.telp or ''
            initial_alamat = request.user.anggota.alamat or ''

    context = {
        'title': 'Checkout Pemesanan - Lesaffrone Bakery',
        'heading': 'Formulir Checkout & Pengiriman',
        'cart_items': cart_items,
        'total_harga': total_harga,
        'ongkir': ongkir,
        'grand_total': grand_total,
        'initial_nama': initial_nama,
        'initial_telp': initial_telp,
        'initial_email': initial_email,
        'initial_alamat': initial_alamat,
    }
    return render(request, 'pembayaran/checkout.html', context)


# ─────────────────────────────────────────────────────────────
#  SANDBOX PAYMENT GATEWAY SIMULATOR (FINTECH SIMULATION)
# ─────────────────────────────────────────────────────────────

def payment_sandbox_view(request, order_id):
    """
    Tampilan simulator antarmuka Payment Gateway Sandbox.
    Mirip dengan antarmuka Midtrans Snap / Xendit / DOKU Sandbox.
    """
    pesanan = get_object_or_404(Pesanan, id=order_id)
    gateway = get_object_or_404(TransaksiPaymentGateway, pesanan=pesanan)

    # Jika sudah dibayar, langsung bawa ke invoice
    if pesanan.status == 'dibayar' or gateway.status_transaksi == 'settlement':
        messages.info(request, 'Pesanan ini sudah berhasil dibayar!')
        return redirect('order_invoice', order_id=pesanan.id)

    context = {
        'title': f'Sandbox Payment Gateway - {pesanan.nomor_pesanan}',
        'pesanan': pesanan,
        'gateway': gateway,
        'items': pesanan.items.all(),
    }
    return render(request, 'pembayaran/sandbox_gateway.html', context)


def payment_simulate_action(request, order_id, action):
    """
    Simulasi aksi status pembayaran sandbox:
    - 'success' / 'settlement' -> Bayar Berhasil
    - 'deny' / 'failed'        -> Pembayaran Ditolak / Gagal
    - 'expire'                 -> Waktu Habis / Kadaluarsa
    - 'cancel'                 -> Dibatalkan Pelanggan
    """
    pesanan = get_object_or_404(Pesanan, id=order_id)
    gateway = get_object_or_404(TransaksiPaymentGateway, pesanan=pesanan)

    now = timezone.now()

    if action in ['success', 'settlement']:
        gateway.status_transaksi = 'settlement'
        gateway.status_code = '200'
        gateway.status_message = 'Pembayaran sandbox berhasil diverifikasi (Settlement)'
        gateway.settled_at = now
        gateway.save()

        pesanan.status = 'dibayar'
        pesanan.waktu_bayar = now
        pesanan.save()

        # Kurangi stok produk secara otomatis
        for item in pesanan.items.all():
            if item.produk:
                if item.produk.stok >= item.jumlah:
                    item.produk.stok -= item.jumlah
                else:
                    item.produk.stok = 0
                item.produk.save(update_fields=['stok'])

        messages.success(request, f'🎉 Pembayaran Sandbox Berhasil! Invoice {pesanan.nomor_pesanan} telah lunas.')
        return redirect('order_invoice', order_id=pesanan.id)

    elif action in ['deny', 'failed']:
        gateway.status_transaksi = 'deny'
        gateway.status_code = '202'
        gateway.status_message = 'Pembayaran sandbox ditolak atau kartu ditolak'
        gateway.save()

        pesanan.status = 'dibatalkan'
        pesanan.save()
        messages.error(request, '⚠️ Simulasi: Pembayaran Ditolak / Gagal.')
        return redirect('payment_sandbox', order_id=pesanan.id)

    elif action == 'expire':
        gateway.status_transaksi = 'expire'
        gateway.status_code = '408'
        gateway.status_message = 'Waktu pembayaran sandbox telah kadaluarsa'
        gateway.expired_at = now
        gateway.save()

        pesanan.status = 'dibatalkan'
        pesanan.save()
        messages.warning(request, '⏳ Simulasi: Pembayaran telah kadaluarsa (Expired).')
        return redirect('payment_sandbox', order_id=pesanan.id)

    elif action == 'cancel':
        gateway.status_transaksi = 'cancel'
        gateway.status_code = '200'
        gateway.status_message = 'Pembayaran dibatalkan oleh pengguna'
        gateway.save()

        pesanan.status = 'dibatalkan'
        pesanan.save()
        messages.info(request, 'Transaksi pembayaran dibatalkan.')
        return redirect('katalog')

    return redirect('payment_sandbox', order_id=pesanan.id)


# ─────────────────────────────────────────────────────────────
#  INVOICE / BUKTI PEMBAYARAN RESMI
# ─────────────────────────────────────────────────────────────

def order_invoice_view(request, order_id):
    """Halaman Invoice resmi pesanan yang siap dicetak/diunduh."""
    pesanan = get_object_or_404(Pesanan, id=order_id)
    gateway = getattr(pesanan, 'transaksi_gateway', None)

    context = {
        'title': f'Invoice {pesanan.nomor_pesanan} - Lesaffrone Bakery',
        'pesanan': pesanan,
        'gateway': gateway,
        'items': pesanan.items.all(),
    }
    return render(request, 'pembayaran/invoice.html', context)


# ─────────────────────────────────────────────────────────────
#  RIWAYAT PESANAN (CUSTOMER & ADMIN)
# ─────────────────────────────────────────────────────────────

@login_required
def riwayat_pesanan_view(request):
    """Daftar riwayat pesanan milik pelanggan yang sedang login."""
    pesanan_list = Pesanan.objects.filter(user=request.user).order_by('-waktu_pesan')
    context = {
        'title': 'Riwayat Pesanan Saya - Lesaffrone Bakery',
        'heading': 'Riwayat Pesanan Anda',
        'pesanan_list': pesanan_list,
    }
    return render(request, 'pembayaran/riwayat_pesanan.html', context)


@admin_required
def admin_daftar_pesanan(request):
    """Panel Admin untuk memantau semua pesanan dan transaksi payment gateway."""
    status_filter = request.GET.get('status', '')
    pesanan_list = Pesanan.objects.select_related('user').prefetch_related('items', 'transaksi_gateway').all()

    if status_filter:
        pesanan_list = pesanan_list.filter(status=status_filter)

    total_semua = Pesanan.objects.count()
    total_dibayar = Pesanan.objects.filter(status='dibayar').count()
    total_menunggu = Pesanan.objects.filter(status='menunggu_pembayaran').count()

    context = {
        'title': 'Kelola Pesanan & Gateway - Admin Lesaffrone',
        'heading': 'Manajemen Pesanan & Transaksi Gateway',
        'pesanan_list': pesanan_list,
        'status_filter': status_filter,
        'total_semua': total_semua,
        'total_dibayar': total_dibayar,
        'total_menunggu': total_menunggu,
    }
    return render(request, 'admin_super/katalog/daftar_pesanan.html', context)


@admin_required
def admin_update_status_pesanan(request, order_id):
    """Admin mengubah status pengiriman pesanan (misal: diproses, dikirim, selesai)."""
    pesanan = get_object_or_404(Pesanan, id=order_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Pesanan.STATUS_CHOICES):
            pesanan.status = new_status
            pesanan.save(update_fields=['status'])
            messages.success(request, f'Status pesanan {pesanan.nomor_pesanan} diubah menjadi "{pesanan.get_status_display()}".')
    return redirect('app:admin_pesanan')

