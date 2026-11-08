"""
Helper Script Setup Lengkap Database Toko Roti & Bakery Lesaffrone
Jalankan di PowerShell:
venv\\Scripts\\python.exe setup_database.py
"""
import os
import sys

# Setup environment Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

try:
    import django
    django.setup()
    from django.core.management import call_command
    from django.contrib.auth.models import User
    from app.models import UserAdmin
    import seed_bakery
except Exception as e:
    print(f"❌ Terjadi kesalahan saat inisialisasi Django: {e}")
    sys.exit(1)

def run_setup():
    print("=" * 60)
    print("🥐 SETUP DATABASE E-COMMERCE BAKERY LESAFFRONE")
    print("=" * 60)

    # 1. Jalankan Migrate
    print("\n[1/3] Menjalankan migrasi database (Django migrate)...")
    try:
        call_command('migrate', interactive=False)
        print("  ✅ Migrasi database berhasil!")
    except Exception as e:
        print(f"  ❌ Gagal migrasi: {e}")
        print("  Pastikan MySQL sudah aktif dan database 'db_eccomerce' sudah dibuat.")
        return

    # 2. Buat / Reset Akun Super Admin
    print("\n[2/3] Mengonfigurasi Akun Super Admin...")
    USERNAME = 'ojan'
    PASSWORD = '201601411Ojan'
    EMAIL    = 'ojan@admin.com'
    NAMA     = 'Ojan'

    user = User.objects.filter(username=USERNAME).first()
    if user:
        user.set_password(PASSWORD)
        user.first_name = NAMA
        user.last_name  = 'Super Admin'
        user.is_superuser = True
        user.is_staff     = True
        user.is_active    = True
        user.save()
        print(f"  ✅ Akun '{USERNAME}' berhasil di-update sebagai Super Admin.")
    else:
        user = User.objects.create_superuser(
            username=USERNAME,
            email=EMAIL,
            password=PASSWORD,
            first_name=NAMA,
            last_name='Super Admin'
        )
        print(f"  ✅ Akun Super Admin '{USERNAME}' berhasil dibuat.")

    # Profil UserAdmin
    UserAdmin.objects.get_or_create(
        username=user,
        defaults={'telp': '081234567890', 'gender': 'Laki-laki'}
    )
    print("  ✅ Profil UserAdmin tersimpan.")

    # 3. Seeding Produk Dummy Bakery (Gambar, Harga, Nama, Deskripsi)
    print("\n[3/3] Memasukkan Data Dummy Produk & Kategori Bakery Lengkap...")
    try:
        seed_bakery.seed_lengkap()
    except Exception as e:
        print(f"  ❌ Gagal seeding: {e}")

    print("\n" + "=" * 60)
    print("🎉 SEMUA SETUP DATABASE TELAH SELESAI!")
    print("=" * 60)
    print("Kredensial Login:")
    print(f"  • Username : {USERNAME}")
    print(f"  • Password : {PASSWORD}")
    print(f"  • Role     : Super Admin")
    print("\nLangkah selanjutnya, jalankan server web:")
    print("  venv\\Scripts\\python.exe manage.py runserver")
    print("Buka browser: http://127.0.0.1:8000")
    print("=" * 60)

if __name__ == '__main__':
    run_setup()

