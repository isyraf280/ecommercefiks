from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from app.decorators_admin import admin_required
from .models import Produk, KategoriProduk
from .form_produk import FormProduk, FormKategori


# ─── ADMIN: Daftar Semua Produk ───────────────────────────────
@admin_required
def admin_katalog(request):
    q = request.GET.get('q', '').strip()
    kategori_filter = request.GET.get('kategori', '')

    produk_list = Produk.objects.select_related('kategori').all()

    if q:
        produk_list = produk_list.filter(
            Q(nama_produk__icontains=q) | Q(deskripsi__icontains=q)
        )
    if kategori_filter:
        produk_list = produk_list.filter(kategori__id=kategori_filter)

    kategori_all = KategoriProduk.objects.filter(aktif=True)

    context = {
        'title': 'Kelola Katalog Produk',
        'heading': 'Manajemen Katalog Produk',
        'produk_list': produk_list,
        'kategori_all': kategori_all,
        'q': q,
        'kategori_filter': kategori_filter,
        'total_produk': Produk.objects.count(),
        'total_tersedia': Produk.objects.filter(tersedia=True).count(),
        'total_habis': Produk.objects.filter(stok=0).count(),
    }
    return render(request, 'admin_super/katalog/katalog_produk.html', context)


# ─── ADMIN: Tambah Produk ─────────────────────────────────────
@admin_required
def admin_tambah_produk(request):
    if request.method == 'POST':
        form = FormProduk(request.POST, request.FILES)
        if form.is_valid():
            produk = form.save()
            messages.success(request, f'Produk "{produk.nama_produk}" berhasil ditambahkan!')
            return redirect('app:admin_katalog')
        else:
            messages.error(request, 'Gagal menambahkan produk. Periksa isian form.')
    else:
        form = FormProduk()

    context = {
        'title': 'Tambah Produk',
        'heading': 'Tambah Produk Baru',
        'form': form,
        'action': 'tambah',
    }
    return render(request, 'admin_super/katalog/form_produk.html', context)


# ─── ADMIN: Edit Produk ───────────────────────────────────────
@admin_required
def admin_edit_produk(request, slug):
    produk = get_object_or_404(Produk, slug=slug)
    if request.method == 'POST':
        form = FormProduk(request.POST, request.FILES, instance=produk)
        if form.is_valid():
            form.save()
            messages.success(request, f'Produk "{produk.nama_produk}" berhasil diperbarui!')
            return redirect('app:admin_katalog')
        else:
            messages.error(request, 'Gagal memperbarui produk. Periksa isian form.')
    else:
        form = FormProduk(instance=produk)

    context = {
        'title': 'Edit Produk',
        'heading': f'Edit Produk: {produk.nama_produk}',
        'form': form,
        'produk': produk,
        'action': 'edit',
    }
    return render(request, 'admin_super/katalog/form_produk.html', context)


# ─── ADMIN: Hapus Produk ──────────────────────────────────────
@admin_required
def admin_hapus_produk(request, slug):
    produk = get_object_or_404(Produk, slug=slug)
    if request.method == 'POST':
        nama = produk.nama_produk
        produk.delete()
        messages.success(request, f'Produk "{nama}" berhasil dihapus.')
        return redirect('app:admin_katalog')
    context = {
        'title': 'Hapus Produk',
        'heading': 'Konfirmasi Hapus Produk',
        'produk': produk,
    }
    return render(request, 'admin_super/katalog/hapus_produk.html', context)


# ─── ADMIN: Kelola Kategori ───────────────────────────────────
@admin_required
def admin_kategori(request):
    kategori_list = KategoriProduk.objects.all()
    context = {
        'title': 'Kelola Kategori',
        'heading': 'Manajemen Kategori Produk',
        'kategori_list': kategori_list,
    }
    return render(request, 'admin_super/katalog/kategori.html', context)


@admin_required
def admin_tambah_kategori(request):
    if request.method == 'POST':
        form = FormKategori(request.POST)
        if form.is_valid():
            kat = form.save()
            messages.success(request, f'Kategori "{kat.nama}" berhasil ditambahkan!')
            return redirect('app:admin_kategori')
        else:
            messages.error(request, 'Gagal menambahkan kategori.')
    else:
        form = FormKategori()
    context = {
        'title': 'Tambah Kategori',
        'heading': 'Tambah Kategori Baru',
        'form': form,
    }
    return render(request, 'admin_super/katalog/form_kategori.html', context)


@admin_required
def admin_edit_kategori(request, pk):
    kat = get_object_or_404(KategoriProduk, pk=pk)
    if request.method == 'POST':
        form = FormKategori(request.POST, instance=kat)
        if form.is_valid():
            form.save()
            messages.success(request, f'Kategori "{kat.nama}" berhasil diperbarui!')
            return redirect('app:admin_kategori')
        else:
            messages.error(request, 'Gagal memperbarui kategori.')
    else:
        form = FormKategori(instance=kat)
    context = {
        'title': 'Edit Kategori',
        'heading': f'Edit Kategori: {kat.nama}',
        'form': form,
        'kategori': kat,
    }
    return render(request, 'admin_super/katalog/form_kategori.html', context)


@admin_required
def admin_hapus_kategori(request, pk):
    kat = get_object_or_404(KategoriProduk, pk=pk)
    if request.method == 'POST':
        nama = kat.nama
        kat.delete()
        messages.success(request, f'Kategori "{nama}" berhasil dihapus.')
        return redirect('app:admin_kategori')
    context = {
        'title': 'Hapus Kategori',
        'heading': 'Konfirmasi Hapus Kategori',
        'kategori': kat,
    }
    return render(request, 'admin_super/katalog/hapus_kategori.html', context)


# ─── FRONT END WEBSITE: LANDING PAGE PUBLIK ───────────────────
def landing_page(request):
    # Auto-seed produk jika database masih kosong
    if Produk.objects.count() == 0:
        try:
            import seed_bakery
            seed_bakery.seed_lengkap()
        except Exception as e:
            print(f"[Auto-seed Warning] {e}")

    # Pastikan setiap produk memiliki foto
    MAP_FOTO = {
        'sobek': 'produk/roti_sobek_cokelat_lumer.jpg',
        'sisir': 'produk/roti_sisir_butter_mentega.jpg',
        'croissant': 'produk/classic_french_croissant.jpg',
        'pain au chocolat': 'produk/pain_au_chocolat.jpg',
        'danish': 'produk/danish_pastry_blueberry.jpg',
        'gandum': 'produk/roti_tawar_gandum_utuh.jpg',
        'hokkaido': 'produk/roti_tawar_susu_hokkaido.jpg',
        'bolu gulung': 'produk/bolu_gulung_keju_spesial.jpg',
        'chiffon': 'produk/chiffon_cake_pandan_suji.jpg',
        'abon': 'produk/roti_abon_sapi_mayo.jpg',
        'sosis': 'produk/roti_sosis_keju_panggang.jpg',
        'keju krim': 'produk/roti_keju_krim_manis.jpg',
    }
    for p in Produk.objects.all():
        nama_lower = p.nama_produk.lower()
        for key, rel_path in MAP_FOTO.items():
            if key in nama_lower:
                if not p.foto or p.foto.name != rel_path:
                    p.foto = rel_path
                    p.save(update_fields=['foto'])
                break

    q = request.GET.get('q', '').strip()
    kategori_slug = request.GET.get('kategori', '')

    produk_list = Produk.objects.select_related('kategori').filter(tersedia=True)

    if q:
        produk_list = produk_list.filter(
            Q(nama_produk__icontains=q) | Q(deskripsi__icontains=q) | Q(bahan__icontains=q)
        )
    if kategori_slug:
        produk_list = produk_list.filter(kategori__slug=kategori_slug)

    kategori_all = KategoriProduk.objects.filter(aktif=True)
    produk_unggulan = Produk.objects.filter(tersedia=True, unggulan=True)[:8]

    context = {
        'title': 'Toko Roti & Bakery Lesaffrone - Kelezatan Roti Segar Setiap Hari',
        'produk_list': produk_list,
        'kategori_all': kategori_all,
        'produk_unggulan': produk_unggulan,
        'q': q,
        'kategori_slug': kategori_slug,
        'total_produk': Produk.objects.filter(tersedia=True).count(),
        'total_kategori': KategoriProduk.objects.filter(aktif=True).count(),
    }
    return render(request, 'frontend/index.html', context)


# ─── PENGGUNA: Lihat Katalog ──────────────────────────────────
def katalog_pengguna(request):
    # 1. Auto-seed produk jika database masih kosong
    if Produk.objects.count() == 0:
        try:
            import seed_bakery
            seed_bakery.seed_lengkap()
        except Exception as e:
            print(f"[Auto-seed Warning] {e}")

    # 2. Pastikan SETIAP produk memiliki foto yang benar di database
    MAP_FOTO = {
        'sobek': 'produk/roti_sobek_cokelat_lumer.jpg',
        'sisir': 'produk/roti_sisir_butter_mentega.jpg',
        'croissant': 'produk/classic_french_croissant.jpg',
        'pain au chocolat': 'produk/pain_au_chocolat.jpg',
        'danish': 'produk/danish_pastry_blueberry.jpg',
        'gandum': 'produk/roti_tawar_gandum_utuh.jpg',
        'hokkaido': 'produk/roti_tawar_susu_hokkaido.jpg',
        'bolu gulung': 'produk/bolu_gulung_keju_spesial.jpg',
        'chiffon': 'produk/chiffon_cake_pandan_suji.jpg',
        'abon': 'produk/roti_abon_sapi_mayo.jpg',
        'sosis': 'produk/roti_sosis_keju_panggang.jpg',
        'keju krim': 'produk/roti_keju_krim_manis.jpg',
    }
    for p in Produk.objects.all():
        nama_lower = p.nama_produk.lower()
        for key, rel_path in MAP_FOTO.items():
            if key in nama_lower:
                if not p.foto or p.foto.name != rel_path:
                    p.foto = rel_path
                    p.save(update_fields=['foto'])
                break

    q = request.GET.get('q', '').strip()
    kategori_slug = request.GET.get('kategori', '')
    sort = request.GET.get('sort', 'terbaru')

    produk_list = Produk.objects.select_related('kategori').filter(tersedia=True)

    if q:
        produk_list = produk_list.filter(
            Q(nama_produk__icontains=q) | Q(deskripsi__icontains=q) | Q(bahan__icontains=q)
        )

    selected_kategori = None
    if kategori_slug:
        produk_list = produk_list.filter(kategori__slug=kategori_slug)
        selected_kategori = KategoriProduk.objects.filter(slug=kategori_slug).first()

    # Pengurutan
    if sort == 'termurah':
        produk_list = produk_list.order_by('harga')
    elif sort == 'termahal':
        produk_list = produk_list.order_by('-harga')
    elif sort == 'nama_asc':
        produk_list = produk_list.order_by('nama_produk')
    elif sort == 'unggulan':
        produk_list = produk_list.order_by('-unggulan', '-dibuat')
    else:  # terbaru
        produk_list = produk_list.order_by('-dibuat')

    kategori_all = KategoriProduk.objects.filter(aktif=True)
    produk_unggulan = Produk.objects.filter(tersedia=True, unggulan=True)[:6]

    context = {
        'title': 'Katalog Roti & Bakery Lesaffrone',
        'heading': 'Katalog Roti & Bakery Lengkap',
        'produk_list': produk_list,
        'kategori_all': kategori_all,
        'selected_kategori': selected_kategori,
        'produk_unggulan': produk_unggulan,
        'q': q,
        'kategori_slug': kategori_slug,
        'sort': sort,
        'total_ditemukan': produk_list.count(),
        'total_semua': Produk.objects.filter(tersedia=True).count(),
    }
    return render(request, 'pengguna/katalog.html', context)


# ─── ACTION: SEED DUMMY MANUAL ────────────────────────────────
def seed_katalog_view(request):
    try:
        from django.core.management import call_command
        call_command('migrate', interactive=False)
        import seed_bakery
        seed_bakery.seed_lengkap()
        messages.success(request, '🎉 Berhasil! Migrasi database & 12 Produk Dummy Roti & Bakery beserta gambarnya telah disimpan ke database.')
    except Exception as e:
        messages.error(request, f'Gagal inisialisasi database: {e}')
    return redirect('katalog')


# ─── DETAIL PRODUK (Publik & Terdaftar) ────────────────────────
def detail_produk(request, slug):
    produk = get_object_or_404(Produk, slug=slug, tersedia=True)
    produk_terkait = Produk.objects.filter(
        kategori=produk.kategori, tersedia=True
    ).exclude(pk=produk.pk)[:4]

    context = {
        'title': f'{produk.nama_produk} - Lesaffrone Bakery',
        'heading': 'Detail Produk',
        'produk': produk,
        'produk_terkait': produk_terkait,
    }
    return render(request, 'pengguna/detail_produk.html', context)


# ─── HALAMAN INFORMASI ARTISAN: ABOUT, JOURNAL, CONTACT ────────
def about_page(request):
    """Halaman About / Tentang Kami Lesaffrone Artisan Bakery"""
    context = {
        'title': 'About Us — Lesaffrone Artisan Bakery',
        'heading': 'Our Story & Philosophy',
    }
    return render(request, 'frontend/about.html', context)


def story_page(request):
    """Alias untuk backwards-compatibility"""
    return about_page(request)


def journal_page(request):
    """Halaman Journal / Catatan Dapur Lesaffrone"""
    articles = [
        {
            'slug': 'why-best-croissant-takes-time',
            'tag': 'Behind the Bake',
            'read_time': '5 min read',
            'title': 'Why the best croissant takes a little more time.',
            'excerpt': 'Di balik ratusan lapisan renyah dan rongga honeycomb yang menawan, tersimpan proses laminasi 24 jam dengan butter berkualitas dan kesabaran para baker.',
            'image': 'https://images.unsplash.com/photo-1530610476181-d83430b64dcd?auto=format&fit=crop&w=850&q=85',
            'date': '12 November 2026',
            'author': 'Chef Pastry Ojan',
        },
        {
            'slug': 'butter-flour-and-honest-ingredients',
            'tag': 'Our Ingredients',
            'read_time': '3 min read',
            'title': 'A little note about butter, flour & everything in between.',
            'excerpt': 'Kami tidak menggunakan pengembang instan atau pemutih tepung. Segala yang kami sajikan berawal dari bahan murni pilihan yang diproses secara etis.',
            'image': 'https://images.unsplash.com/photo-1509365465985-25d11c17e812?auto=format&fit=crop&w=750&q=85',
            'date': '08 November 2026',
            'author': 'Lesaffrone Team',
        },
        {
            'slug': 'make-room-for-slower-morning',
            'tag': 'Slow Living',
            'read_time': '4 min read',
            'title': 'Make room for a slower, sweeter kind of morning.',
            'excerpt': 'Secangkir seduhan kopi hangat, sepotong sourdough panggang dengan taburan garam laut. Ritual kecil yang mengubah pagi biasa jadi berkah istimewa.',
            'image': 'https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=750&q=85',
            'date': '03 November 2026',
            'author': 'Sarah Miller',
        },
        {
            'slug': 'sourdough-starter-care-guide',
            'tag': 'Kitchen Guide',
            'read_time': '6 min read',
            'title': 'Merawat starter sourdough liar di iklim tropis Indonesia.',
            'excerpt': 'Panduan praktis menjaga suhu ragi alami tetap aktif dan beraroma buah segar tanpa menjadi terlalu asam saat cuaca sedang panas.',
            'image': 'https://images.unsplash.com/photo-1589367920969-ab8e050bbb04?auto=format&fit=crop&w=750&q=85',
            'date': '28 Oktober 2026',
            'author': 'Master Baker Anto',
        },
        {
            'slug': 'pairing-pastries-with-coffee',
            'tag': 'Morning Rituals',
            'read_time': '4 min read',
            'title': 'Seni memasangkan pastry renyah dengan karakter kopi nusantara.',
            'excerpt': 'Dari Toraja yang berkarakter rempah hingga Gayo yang fruity, temukan padanan pastry yang membuat selera Anda menari gembira.',
            'image': 'https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?auto=format&fit=crop&w=750&q=85',
            'date': '20 Oktober 2026',
            'author': 'Barista Team',
        },
        {
            'slug': 'behind-the-scenes-night-bakers',
            'tag': 'Artisan Life',
            'read_time': '7 min read',
            'title': 'Malam sunyi para peracik roti: jam 03.00 di dapur Lesaffrone.',
            'excerpt': 'Saat seisi kota terlelap dalam mimpi, oven kami mulai menyala. Inilah cerita tentang dedikasi menghasilkan roti yang masih hangat di pagi Anda.',
            'image': 'https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=750&q=85',
            'date': '15 Oktober 2026',
            'author': 'Lesaffrone Team',
        },
    ]
    context = {
        'title': 'The Little Journal — Lesaffrone Artisan Bakery',
        'heading': 'Notes from our Kitchen',
        'articles': articles,
    }
    return render(request, 'frontend/journal.html', context)


def contact_page(request):
    """Halaman Contact / Kontak Lesaffrone"""
    context = {
        'title': 'Contact Us — Lesaffrone Artisan Bakery',
        'heading': 'Say Hello, Buttercup',
    }
    return render(request, 'frontend/contact.html', context)


