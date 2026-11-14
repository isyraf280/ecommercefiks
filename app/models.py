from django.db import models
from django.contrib.auth.models import User
import uuid
from django.utils import timezone
import os
from django.conf import settings
from django.utils.text import slugify

User.add_to_class("__str__", lambda self: f"{self.username} - {self.first_name}")

class Provinsi(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nama_provinsi = models.CharField(max_length=100, unique=True, verbose_name='Nama Provinsi')
    aktif = models.BooleanField(default=True, verbose_name='Aktif')

    class Meta:
        verbose_name = 'Provinsi'
        verbose_name_plural = 'Provinsi'
        ordering = ['nama_provinsi']

    def __str__(self):
        return f"{self.nama_provinsi}"

def rename_photo_anggota(instance, filename):
    ext = filename.split('.')[-1]
    username = instance.user.username
    timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
    new_filename = f"{username}_{timestamp}.{ext}"
    return os.path.join('img_profile/anggota/', new_filename)

class UserPengguna(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)    
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name="anggota")
    telp = models.CharField(max_length=15)
    gender = models.CharField(max_length=15, null=True, blank=True, choices=[
        ('Laki-laki', 'Laki-laki'),
        ('Perempuan', 'Perempuan'),
    ]) 
    alamat = models.CharField(max_length=50, null=True, blank=True)
    photo = models.ImageField(upload_to=rename_photo_anggota, null=True, blank=True)
    provinsi_anggota = models.ForeignKey(Provinsi, on_delete=models.SET_NULL, null=True, blank=True)
    jafung = models.CharField(max_length=100, null=True, blank=True)
    nuptk = models.CharField(max_length=20, null=True, blank=True, verbose_name='NUPTK')
    bidang_keahlian = models.CharField(max_length=100, null=True, blank=True)
    link_sinta = models.URLField(max_length=200, verbose_name='Link Sinta')
    link_scopus = models.URLField(max_length=200, null=True, blank=True, verbose_name='Link Scopus')
    link_google_scholar = models.URLField(max_length=200, null=True, blank=True, verbose_name='Link Google Scholar')
    link_orcid = models.URLField(max_length=200, null=True, blank=True, verbose_name='Link ORCID')


    class Meta:
        verbose_name = 'Anggota'
        verbose_name_plural = 'Anggota'

    def save(self, *args, **kwargs):
        try:
            old_instance = UserPengguna.objects.get(pk=self.pk)
            if old_instance.photo and old_instance.photo != self.photo:
                old_photo_path = os.path.join(
                    settings.MEDIA_ROOT,
                    old_instance.photo.name
                )
                if os.path.isfile(old_photo_path):
                    os.remove(old_photo_path)
        except UserPengguna.DoesNotExist:
            pass
        super().save(*args, **kwargs)

def rename_photo_admin(instance, filename):
    ext = filename.split('.')[-1]
    username = instance.username
    timestamp = timezone.now().strftime('%Y%m%d%H%M%S') 
    new_filename = f"{username}_{timestamp}.{ext}"
    return os.path.join('img_profile/admin/', new_filename)  


class UserAdmin(models.Model):
    username = models.OneToOneField(User, on_delete=models.CASCADE, to_field="username", primary_key=True)
    telp = models.CharField(max_length=15)
    gender = models.CharField(max_length=15, choices=[
        ('Laki-laki', 'Laki-laki'),
        ('Perempuan', 'Perempuan'),
    ])
    photo = models.ImageField(upload_to=rename_photo_admin)

    def save(self, *args, **kwargs):
        try:
            old_instance = UserAdmin.objects.get(pk=self.pk)
            if old_instance.photo and old_instance.photo != self.photo:
                old_photo_path = os.path.join(settings.MEDIA_ROOT, old_instance.photo.name)
                if os.path.isfile(old_photo_path):
                    os.remove(old_photo_path)
        except UserAdmin.DoesNotExist:
            pass  

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username}"


# ─────────────────────────────────────────────────────────────
#  KATALOG PRODUK ROTI & BAKERY
# ─────────────────────────────────────────────────────────────

class KategoriProduk(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nama = models.CharField(max_length=100, unique=True, verbose_name='Nama Kategori')
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    deskripsi = models.TextField(blank=True, null=True, verbose_name='Deskripsi')
    aktif = models.BooleanField(default=True, verbose_name='Aktif')
    dibuat = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Kategori Produk'
        verbose_name_plural = 'Kategori Produk'
        ordering = ['nama']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nama)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nama

    @property
    def nama_kategori(self):
        return self.nama


def rename_foto_produk(instance, filename):
    ext = filename.split('.')[-1]
    slug = instance.slug or slugify(instance.nama_produk)
    timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
    new_filename = f"{slug}_{timestamp}.{ext}"
    return os.path.join('produk/', new_filename)


class Produk(models.Model):
    SATUAN_CHOICES = [
        ('pcs', 'Pcs'),
        ('loyang', 'Loyang'),
        ('kotak', 'Kotak'),
        ('lusin', 'Lusin'),
        ('kg', 'Kilogram'),
        ('gram', 'Gram'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    kategori = models.ForeignKey(
        KategoriProduk, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='produk', verbose_name='Kategori'
    )
    nama_produk = models.CharField(max_length=200, verbose_name='Nama Produk')
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    deskripsi = models.TextField(blank=True, null=True, verbose_name='Deskripsi Produk')
    bahan = models.TextField(blank=True, null=True, verbose_name='Bahan / Komposisi')
    harga = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Harga (Rp)')
    stok = models.PositiveIntegerField(default=0, verbose_name='Stok')
    satuan = models.CharField(max_length=20, choices=SATUAN_CHOICES, default='pcs', verbose_name='Satuan')
    berat_gram = models.PositiveIntegerField(null=True, blank=True, verbose_name='Berat (gram)')
    foto = models.ImageField(upload_to=rename_foto_produk, null=True, blank=True, verbose_name='Foto Produk')
    tersedia = models.BooleanField(default=True, verbose_name='Tersedia / Aktif')
    unggulan = models.BooleanField(default=False, verbose_name='Produk Unggulan')
    dibuat = models.DateTimeField(auto_now_add=True)
    diperbarui = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Produk'
        verbose_name_plural = 'Produk'
        ordering = ['-dibuat']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.nama_produk)
            slug = base_slug
            counter = 1
            while Produk.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        # Hapus foto lama saat diganti
        try:
            old = Produk.objects.get(pk=self.pk)
            if old.foto and old.foto != self.foto:
                old_path = os.path.join(settings.MEDIA_ROOT, old.foto.name)
                if os.path.isfile(old_path):
                    os.remove(old_path)
        except Produk.DoesNotExist:
            pass

        super().save(*args, **kwargs)

    def __str__(self):
        return self.nama_produk

    @property
    def harga_rupiah(self):
        return f"Rp {self.harga:,.0f}"


# ─────────────────────────────────────────────────────────────
#  CHECKOUT & SANDBOX PAYMENT GATEWAY
# ─────────────────────────────────────────────────────────────

class Pesanan(models.Model):
    STATUS_CHOICES = [
        ('menunggu_pembayaran', 'Menunggu Pembayaran'),
        ('dibayar', 'Sudah Dibayar'),
        ('diproses', 'Sedang Diproses'),
        ('dikirim', 'Sedang Dikirim'),
        ('selesai', 'Selesai'),
        ('dibatalkan', 'Dibatalkan'),
    ]

    METODE_CHOICES = [
        ('qris', 'QRIS (GoPay, OVO, ShopeePay, Dana, BCA Mobile)'),
        ('va_bca', 'BCA Virtual Account'),
        ('va_mandiri', 'Mandiri Virtual Account'),
        ('va_bri', 'BRI Virtual Account'),
        ('kartu_kredit', 'Kartu Kredit / Debit Online (Sandbox)'),
        ('gopay', 'GoPay E-Wallet'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nomor_pesanan = models.CharField(max_length=50, unique=True, verbose_name='Nomor Invoice / Pesanan')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='pesanan')
    nama_pelanggan = models.CharField(max_length=150, verbose_name='Nama Lengkap Penerima')
    email = models.EmailField(blank=True, null=True, verbose_name='Email Penerima')
    telepon = models.CharField(max_length=25, verbose_name='Nomor WhatsApp / Telp')
    alamat_pengiriman = models.TextField(verbose_name='Alamat Pengiriman Lengkap')
    catatan = models.TextField(blank=True, null=True, verbose_name='Catatan Pesanan')

    total_harga = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Total Harga Produk')
    ongkir = models.DecimalField(max_digits=12, decimal_places=2, default=10000, verbose_name='Biaya Pengiriman')
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Grand Total (Rp)')

    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='menunggu_pembayaran', verbose_name='Status Pesanan')
    metode_pembayaran = models.CharField(max_length=30, choices=METODE_CHOICES, default='qris', verbose_name='Metode Pembayaran')

    waktu_pesan = models.DateTimeField(auto_now_add=True, verbose_name='Waktu Pemesanan')
    waktu_bayar = models.DateTimeField(null=True, blank=True, verbose_name='Waktu Pembayaran')

    class Meta:
        verbose_name = 'Pesanan'
        verbose_name_plural = 'Daftar Pesanan'
        ordering = ['-waktu_pesan']

    def __str__(self):
        return f"{self.nomor_pesanan} - {self.nama_pelanggan} ({self.get_status_display()})"

    @property
    def grand_total_rupiah(self):
        return f"Rp {self.grand_total:,.0f}"

    @property
    def ongkir_rupiah(self):
        return f"Rp {self.ongkir:,.0f}"

    @property
    def total_harga_rupiah(self):
        return f"Rp {self.total_harga:,.0f}"


class ItemPesanan(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pesanan = models.ForeignKey(Pesanan, on_delete=models.CASCADE, related_name='items')
    produk = models.ForeignKey(Produk, on_delete=models.SET_NULL, null=True, blank=True, related_name='item_pesanan')
    nama_produk = models.CharField(max_length=200)
    harga_satuan = models.DecimalField(max_digits=12, decimal_places=2)
    jumlah = models.PositiveIntegerField(default=1)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.jumlah}x {self.nama_produk}"

    @property
    def subtotal_rupiah(self):
        return f"Rp {self.subtotal:,.0f}"

    @property
    def harga_satuan_rupiah(self):
        return f"Rp {self.harga_satuan:,.0f}"


class TransaksiPaymentGateway(models.Model):
    STATUS_TRANS_CHOICES = [
        ('pending', 'Pending (Menunggu Bayar)'),
        ('settlement', 'Settlement (Sukses Dibayar)'),
        ('expire', 'Expired (Kadaluarsa)'),
        ('deny', 'Denied / Failed (Ditolak)'),
        ('cancel', 'Cancelled (Dibatalkan)'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pesanan = models.OneToOneField(Pesanan, on_delete=models.CASCADE, related_name='transaksi_gateway')
    transaction_id = models.CharField(max_length=100, unique=True, verbose_name='ID Transaksi Gateway')
    merchant_id = models.CharField(max_length=50, default='LESAFFRONE-SANDBOX')
    payment_type = models.CharField(max_length=50, verbose_name='Tipe Pembayaran')
    va_number = models.CharField(max_length=60, blank=True, null=True, verbose_name='Nomor Virtual Account')
    bank = models.CharField(max_length=30, blank=True, null=True, verbose_name='Nama Bank')
    qr_string = models.TextField(blank=True, null=True, verbose_name='Data QRIS')

    status_transaksi = models.CharField(max_length=30, choices=STATUS_TRANS_CHOICES, default='pending')
    status_code = models.CharField(max_length=10, default='201')
    status_message = models.CharField(max_length=255, default='Menunggu pembayaran sandbox')

    created_at = models.DateTimeField(auto_now_add=True)
    settled_at = models.DateTimeField(null=True, blank=True)
    expired_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.transaction_id} [{self.get_status_transaksi_display()}] - {self.pesanan.nomor_pesanan}"
