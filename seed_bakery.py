import os
import django
from decimal import Decimal
from PIL import Image, ImageDraw, ImageFont

try:
    from django.apps import apps
    if not apps.ready:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
        django.setup()
except Exception:
    pass

from django.conf import settings
from django.utils.text import slugify
from app.models import KategoriProduk, Produk

# Pastikan folder media/produk ada
PRODUK_DIR = os.path.join(settings.MEDIA_ROOT, 'produk')
os.makedirs(PRODUK_DIR, exist_ok=True)

def get_font(size, bold=False):
    """Mencari font TrueType di Windows, fallback ke default."""
    font_paths = [
        'C:/Windows/Fonts/segoeuib.ttf' if bold else 'C:/Windows/Fonts/segoeui.ttf',
        'C:/Windows/Fonts/arialbd.ttf' if bold else 'C:/Windows/Fonts/arial.ttf',
        'C:/Windows/Fonts/tahomabd.ttf' if bold else 'C:/Windows/Fonts/tahoma.ttf',
    ]
    for p in font_paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()

def buat_gambar_produk(filename, title, category, price, bg_color1, bg_color2, accent_color, icon_text):
    """
    Membuat banner gambar produk berkualitas tinggi (640x440 px).
    """
    filepath = os.path.join(PRODUK_DIR, filename)
    width, height = 640, 440

    img = Image.new('RGB', (width, height), bg_color1)
    draw = ImageDraw.Draw(img)

    # 1. Background Gradient halus
    r1, g1, b1 = Image.new('RGB', (1, 1), bg_color1).getpixel((0, 0))
    r2, g2, b2 = Image.new('RGB', (1, 1), bg_color2).getpixel((0, 0))
    for y in range(height):
        ratio = y / height
        nr = int(r1 * (1 - ratio) + r2 * ratio)
        ng = int(g1 * (1 - ratio) + g2 * ratio)
        nb = int(b1 * (1 - ratio) + b2 * ratio)
        draw.line([(0, y), (width, y)], fill=(nr, ng, nb))

    # 2. Lingkaran cahaya ambient di belakang
    draw.ellipse([width//2 - 180, 40, width//2 + 180, 400], fill=accent_color)
    draw.ellipse([width//2 - 140, 70, width//2 + 140, 350], fill=(255, 255, 255, 230))

    # 3. Border garis halus tepi
    draw.rounded_rectangle([16, 16, width - 16, height - 16], radius=20, outline=(255, 255, 255, 120), width=2)

    # 4. Badge Brand Atas
    draw.rounded_rectangle([28, 26, 210, 56], radius=15, fill=(0, 0, 0, 160))
    f_badge = get_font(13, bold=True)
    draw.text((40, 34), "🍞 LESAFFRONE", font=f_badge, fill=(255, 215, 0))

    # 5. Badge Kategori Kanan Atas
    f_cat = get_font(12, bold=True)
    cat_text = category.upper()
    cat_bbox = draw.textbbox((0, 0), cat_text, font=f_cat)
    cat_w = cat_bbox[2] - cat_bbox[0]
    draw.rounded_rectangle([width - cat_w - 46, 26, width - 26, 56], radius=15, fill=(255, 255, 255, 230))
    draw.text((width - cat_w - 36, 34), cat_text, font=f_cat, fill=(180, 60, 10))

    # 6. Ikon / Gambar Karakter Roti Tengah
    f_icon = get_font(76, bold=True)
    ibox = draw.textbbox((0, 0), icon_text, font=f_icon)
    iw = ibox[2] - ibox[0]
    draw.text(((width - iw) // 2, 120), icon_text, font=f_icon, fill=(60, 40, 20))

    # 7. Sub-label "FRESHLY BAKED DAILY"
    f_sub = get_font(12, bold=True)
    sub_text = "✨ FRESH FROM THE OVEN • 100% BUTTER ASLI"
    sbox = draw.textbbox((0, 0), sub_text, font=f_sub)
    sw = sbox[2] - sbox[0]
    draw.text(((width - sw) // 2, 230), sub_text, font=f_sub, fill=(120, 70, 20))

    # 8. Box Bawah untuk Judul & Harga
    draw.rounded_rectangle([26, 280, width - 26, height - 26], radius=16, fill=(255, 255, 255, 245), outline=(240, 230, 215), width=2)

    # Judul Roti
    f_title = get_font(21, bold=True)
    tbox = draw.textbbox((0, 0), title, font=f_title)
    tw = tbox[2] - tbox[0]
    # Jika teks terlalu panjang, gunakan font lebih kecil
    if tw > width - 80:
        f_title = get_font(17, bold=True)
        tbox = draw.textbbox((0, 0), title, font=f_title)
        tw = tbox[2] - tbox[0]
    draw.text(((width - tw) // 2, 298), title, font=f_title, fill=(25, 20, 15))

    # Badge Harga Emas / Emerald
    f_price = get_font(20, bold=True)
    p_text = f"Rp {price:,.0f}"
    pbox = draw.textbbox((0, 0), p_text, font=f_price)
    pw = pbox[2] - pbox[0]
    draw.rounded_rectangle([(width - pw) // 2 - 18, 350, (width + pw) // 2 + 18, 396], radius=12, fill=(194, 65, 12))
    draw.text(((width - pw) // 2, 360), p_text, font=f_price, fill=(255, 255, 255))

    img.save(filepath, format='JPEG', quality=92)
    return f"produk/{filename}"

def seed_lengkap():
    print("🎨 [1/2] Membuat gambar ilustrasi produk bakery...")

    produk_list_data = [
        {
            'kategori': 'Roti Manis & Sobek',
            'nama_produk': 'Roti Sobek Cokelat Lumer',
            'deskripsi': 'Roti sobek legendaris isi 6 potongan super lembut dengan isian cokelat couverture Belgia yang meleleh di setiap sobekannya. Cocok dinikmati bersama kopi atau teh hangat.',
            'bahan': 'Tepung terigu protein tinggi, ragi alami, butter Wijsman, susu segar, cokelat couverture Belgia, telur ayam kampung.',
            'harga': Decimal('28000'),
            'stok': 35,
            'satuan': 'kotak',
            'berat_gram': 400,
            'tersedia': True,
            'unggulan': True,
            'filename': 'roti_sobek_cokelat_lumer.jpg',
            'bg1': '#4A2810', 'bg2': '#2E1505', 'accent': (254, 215, 170),
            'icon': '🍞🍫'
        },
        {
            'kategori': 'Roti Manis & Sobek',
            'nama_produk': 'Roti Sisir Butter Mentega Spesial',
            'deskripsi': 'Roti sisir klasik dengan olesan roombutter Wijsman gurih manis yang melimpah dan meresap sempurna hingga ke serat terdalam roti.',
            'bahan': 'Tepung terigu pilihan, butter roombutter premium, gula pasir tebu, susu bubuk murni, kuning telur.',
            'harga': Decimal('22000'),
            'stok': 30,
            'satuan': 'kotak',
            'berat_gram': 350,
            'tersedia': True,
            'unggulan': True,
            'filename': 'roti_sisir_butter_mentega.jpg',
            'bg1': '#D97706', 'bg2': '#78350F', 'accent': (254, 240, 138),
            'icon': '🧈🍞'
        },
        {
            'kategori': 'Roti Manis & Sobek',
            'nama_produk': 'Roti Keju Krim Manis Lembut',
            'deskripsi': 'Roti manis bundar empuk berselimut parutan keju cheddar tebal dengan isian filling krim keju manis gurih yang lumer saat digigit.',
            'bahan': 'Tepung terigu, cheddar cheese, cream cheese impor, butter, gula, susu evaporasi.',
            'harga': Decimal('14000'),
            'stok': 40,
            'satuan': 'pcs',
            'berat_gram': 120,
            'tersedia': True,
            'unggulan': False,
            'filename': 'roti_keju_krim_manis.jpg',
            'bg1': '#CA8A04', 'bg2': '#713F12', 'accent': (254, 249, 195),
            'icon': '🧀🥯'
        },
        {
            'kategori': 'Roti Tawar & Loaf',
            'nama_produk': 'Roti Tawar Gandum Utuh (Whole Wheat)',
            'deskripsi': 'Roti tawar sehat tinggi serat terbuat dari biji gandum utuh dan madu murni tanpa pengawet. Sangat baik untuk sarapan bergizi keluarga dan pola makan sehat.',
            'bahan': 'Tepung gandum utuh, oat flakes, madu hutan murni, minyak zaitun, ragi, air mineral pegunungan.',
            'harga': Decimal('25000'),
            'stok': 25,
            'satuan': 'bungkus',
            'berat_gram': 450,
            'tersedia': True,
            'unggulan': True,
            'filename': 'roti_tawar_gandum_utuh.jpg',
            'bg1': '#854D0E', 'bg2': '#451A03', 'accent': (254, 215, 170),
            'icon': '🌾🍞'
        },
        {
            'kategori': 'Roti Tawar & Loaf',
            'nama_produk': 'Roti Tawar Susu Hokkaido Toast',
            'deskripsi': 'Roti tawar khas Jepang (Shokupan) dengan campuran susu sapi segar dan fresh cream. Sangat empuk, berserat halus selembut kapas dengan aroma wangi susu.',
            'bahan': 'Tepung terigu Jepang, susu sapi segar Hokkaido blend, fresh cream, butter, yeast.',
            'harga': Decimal('26000'),
            'stok': 20,
            'satuan': 'bungkus',
            'berat_gram': 420,
            'tersedia': True,
            'unggulan': False,
            'filename': 'roti_tawar_susu_hokkaido.jpg',
            'bg1': '#334155', 'bg2': '#0F172A', 'accent': (241, 245, 249),
            'icon': '🥛🍞'
        },
        {
            'kategori': 'Pastry & Croissant',
            'nama_produk': 'Classic French Butter Croissant',
            'deskripsi': 'Croissant artisan asli Prancis berlapis-lapis tipis (flaky) renyah di luar dengan aroma mentega Elle & Vire Prancis yang harum dan rongga lembut di dalam.',
            'bahan': '100% French Elle & Vire Butter, tepung gandum Prancis T55, garam laut Brittany, ragi.',
            'harga': Decimal('20000'),
            'stok': 35,
            'satuan': 'pcs',
            'berat_gram': 90,
            'tersedia': True,
            'unggulan': True,
            'filename': 'classic_french_croissant.jpg',
            'bg1': '#B45309', 'bg2': '#451A03', 'accent': (254, 243, 199),
            'icon': '🥐✨'
        },
        {
            'kategori': 'Pastry & Croissant',
            'nama_produk': 'Pain Au Chocolat Lezat',
            'deskripsi': 'Pastry lipat renyah khas toko roti Prancis dengan dua batang cokelat dark batangan Callebaut 54% yang meleleh saat dipanaskan.',
            'bahan': 'French butter, adonan pastry laminasi, cokelat batangan Callebaut 54%, susu, telur.',
            'harga': Decimal('24000'),
            'stok': 22,
            'satuan': 'pcs',
            'berat_gram': 100,
            'tersedia': True,
            'unggulan': False,
            'filename': 'pain_au_chocolat.jpg',
            'bg1': '#5C2D12', 'bg2': '#2A1104', 'accent': (253, 230, 138),
            'icon': '🥐🍫'
        },
        {
            'kategori': 'Pastry & Croissant',
            'nama_produk': 'Danish Pastry Buah Blueberry',
            'deskripsi': 'Puff pastry renyah bermentega dengan topping custard vanilla lembut dan buah blueberry segar organik dengan selai manis segar.',
            'bahan': 'Puff pastry dough, custard vanilla cream, selai blueberry organik, buah blueberry utuh.',
            'harga': Decimal('23000'),
            'stok': 18,
            'satuan': 'pcs',
            'berat_gram': 110,
            'tersedia': True,
            'unggulan': False,
            'filename': 'danish_pastry_blueberry.jpg',
            'bg1': '#581C87', 'bg2': '#2E1065', 'accent': (237, 233, 254),
            'icon': '🫐🥨'
        },
        {
            'kategori': 'Cake & Bolu Tradisional',
            'nama_produk': 'Bolu Gulung Keju Spesial Lesaffrone',
            'deskripsi': 'Bolu gulung super lembut kaya kuning telur dengan isian butter cream vanila dan parutan keju cheddar melimpah ruah di seluruh permukaan bolu.',
            'bahan': 'Kuning telur banyak, tepung terigu lembut, mentega asin, keju cheddar parut tebal, vanilla extract.',
            'harga': Decimal('65000'),
            'stok': 15,
            'satuan': 'loyang',
            'berat_gram': 600,
            'tersedia': True,
            'unggulan': True,
            'filename': 'bolu_gulung_keju_spesial.jpg',
            'bg1': '#A16207', 'bg2': '#422006', 'accent': (254, 240, 138),
            'icon': '🧀🍰'
        },
        {
            'kategori': 'Cake & Bolu Tradisional',
            'nama_produk': 'Chiffon Cake Pandan Suji Asli',
            'deskripsi': 'Kue chiffon hijau alami dari perasan daun suji dan pandan wangi asli dipadukan dengan santan kelapa kental murni. Teksturnya super ringan dan selembut awan.',
            'bahan': 'Air perasan daun pandan dan daun suji alami, santan kelapa murni kental, tepung kue, telur.',
            'harga': Decimal('55000'),
            'stok': 12,
            'satuan': 'loyang',
            'berat_gram': 550,
            'tersedia': True,
            'unggulan': False,
            'filename': 'chiffon_cake_pandan_suji.jpg',
            'bg1': '#166534', 'bg2': '#052E16', 'accent': (220, 252, 231),
            'icon': '🌿🍰'
        },
        {
            'kategori': 'Roti Gurih & Daging',
            'nama_produk': 'Roti Abon Sapi Floss Mayo Pedas',
            'deskripsi': 'Roti gulung lembut dengan olesan saus mayones pedas gurih racikan istimewa, dibalut taburan abon sapi asli Boyolali yang renyah dan berlimpah.',
            'bahan': 'Tepung terigu, abon sapi kualitas super Boyolali, saus mayones gurih, wijen sangrai, daun bawang.',
            'harga': Decimal('16000'),
            'stok': 30,
            'satuan': 'pcs',
            'berat_gram': 130,
            'tersedia': True,
            'unggulan': True,
            'filename': 'roti_abon_sapi_mayo.jpg',
            'bg1': '#991B1B', 'bg2': '#450A0A', 'accent': (254, 202, 202),
            'icon': '🥩🥖'
        },
        {
            'kategori': 'Roti Gurih & Daging',
            'nama_produk': 'Roti Sosis Keju Panggang (Sausage Bun)',
            'deskripsi': 'Roti gurih empuk dengan sosis sapi bratwurst utuh, siraman saus tomat rempah, saus tartar lembut, dan lelehan keju mozzarella panggang.',
            'bahan': 'Sosis sapi bratwurst premium, keju mozzarella melt, tepung terigu, saus tomat rempah, peterseli cincang.',
            'harga': Decimal('17000'),
            'stok': 30,
            'satuan': 'pcs',
            'berat_gram': 140,
            'tersedia': True,
            'unggulan': False,
            'filename': 'roti_sosis_keju_panggang.jpg',
            'bg1': '#C2410C', 'bg2': '#431407', 'accent': (254, 215, 170),
            'icon': '🌭🧀'
        },
    ]

    # Buat file gambar fisik jika belum ada
    for p in produk_list_data:
        foto_rel_path = f"produk/{p['filename']}"
        filepath = os.path.join(PRODUK_DIR, p['filename'])
        if not os.path.exists(filepath):
            foto_rel_path = buat_gambar_produk(
                filename=p['filename'],
                title=p['nama_produk'],
                category=p['kategori'],
                price=p['harga'],
                bg_color1=p['bg1'],
                bg_color2=p['bg2'],
                accent_color=p['accent'],
                icon_text=p['icon']
            )
            print(f"  [✓] Gambar baru dibuat: {foto_rel_path}")
        else:
            print(f"  [✓] Menggunakan gambar yang sudah ada: {foto_rel_path}")
        p['foto_path'] = foto_rel_path

    # Simpan ke database
    print("\n📦 [2/2] Menyimpan produk ke database MySQL...")
    kategori_cache = {}
    for p in produk_list_data:
        # Kategori
        kat_nama = p['kategori']
        if kat_nama not in kategori_cache:
            kat, _ = KategoriProduk.objects.get_or_create(
                nama=kat_nama,
                defaults={'slug': slugify(kat_nama), 'aktif': True}
            )
            kategori_cache[kat_nama] = kat
        kat = kategori_cache[kat_nama]

        # Produk
        prod, created = Produk.objects.update_or_create(
            nama_produk=p['nama_produk'],
            defaults={
                'slug': slugify(p['nama_produk']),
                'kategori': kat,
                'deskripsi': p['deskripsi'],
                'bahan': p['bahan'],
                'harga': p['harga'],
                'stok': p['stok'],
                'satuan': p['satuan'],
                'berat_gram': p['berat_gram'],
                'foto': p['foto_path'],
                'tersedia': p['tersedia'],
                'unggulan': p['unggulan'],
            }
        )
        aksi = "Dibuat" if created else "Diperbarui"
        print(f"  [+] {aksi}: {prod.nama_produk} -> Rp {prod.harga:,.0f} (Foto: {prod.foto})")

    print("\n" + "=" * 50)
    print("🎉 SEMUA PRODUK + GAMBAR SUDAH TERSIMPAN DI DATABASE!")
    print(f"Total Produk: {Produk.objects.count()}")
    print("=" * 50)

# Alias agar bisa dipanggil seed() atau seed_lengkap()
seed = seed_lengkap

if __name__ == '__main__':
    seed_lengkap()
