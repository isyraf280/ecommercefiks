from django.contrib import admin
from .models import UserPengguna, UserAdmin, Provinsi, Produk, KategoriProduk

# Register your models here.
admin.site.register(UserPengguna)
admin.site.register(UserAdmin)
admin.site.register(Provinsi)


@admin.register(KategoriProduk)
class KategoriProdukAdmin(admin.ModelAdmin):
    list_display = ['nama', 'slug', 'aktif', 'dibuat']
    list_filter = ['aktif']
    search_fields = ['nama']
    prepopulated_fields = {'slug': ('nama',)}


@admin.register(Produk)
class ProdukAdmin(admin.ModelAdmin):
    list_display = ['nama_produk', 'kategori', 'harga', 'stok', 'satuan', 'tersedia', 'unggulan', 'dibuat']
    list_filter = ['tersedia', 'unggulan', 'kategori', 'satuan']
    search_fields = ['nama_produk', 'deskripsi']
    prepopulated_fields = {'slug': ('nama_produk',)}
    list_editable = ['tersedia', 'unggulan', 'stok']
    ordering = ['-dibuat']
