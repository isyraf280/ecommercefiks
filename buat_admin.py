"""
Script untuk membuat atau mereset akun Super Admin
Jalankan: venv\Scripts\python.exe buat_admin.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from app.models import UserAdmin

USERNAME = 'ojan'
PASSWORD = '201601411Ojan'
EMAIL    = 'ojan@admin.com'
NAMA     = 'Ojan'

# ── Cek apakah user sudah ada ──────────────────────────────
user_exists = User.objects.filter(username=USERNAME).exists()

if user_exists:
    user = User.objects.get(username=USERNAME)
    print(f"[INFO] User '{USERNAME}' sudah ada. Mereset password & role...")
    user.set_password(PASSWORD)
    user.first_name = NAMA
    user.last_name  = 'Super Admin'   # ← WAJIB untuk masuk sebagai admin
    user.is_superuser = True
    user.is_staff     = True
    user.is_active    = True
    user.save()
    print(f"[OK] Password direset ke: {PASSWORD}")
    print(f"[OK] last_name diset ke: 'Super Admin'")
    print(f"[OK] is_superuser = True")
else:
    print(f"[INFO] User '{USERNAME}' belum ada. Membuat baru...")
    user = User.objects.create_superuser(
        username   = USERNAME,
        email      = EMAIL,
        password   = PASSWORD,
        first_name = NAMA,
        last_name  = 'Super Admin',
    )
    print(f"[OK] User '{USERNAME}' berhasil dibuat!")

# ── Pastikan UserAdmin record ada ─────────────────────────
useradmin, created = UserAdmin.objects.get_or_create(
    username=user,
    defaults={
        'telp'  : '081234567890',
        'gender': 'Laki-laki',
    }
)
if created:
    print(f"[OK] Profile UserAdmin dibuat.")
else:
    print(f"[OK] Profile UserAdmin sudah ada.")

print()
print("=" * 50)
print(f"  Username  : {USERNAME}")
print(f"  Password  : {PASSWORD}")
print(f"  Role      : Super Admin")
print(f"  Login URL : http://127.0.0.1:8000/login/")
print("=" * 50)
print("Selesai! Silakan login sekarang.")

