from django import forms
from .models import Produk, KategoriProduk


class FormKategori(forms.ModelForm):
    class Meta:
        model = KategoriProduk
        fields = ['nama', 'deskripsi', 'aktif']
        widgets = {
            'nama': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nama kategori...'}),
            'deskripsi': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Deskripsi singkat kategori...'}),
            'aktif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'nama': 'Nama Kategori',
            'deskripsi': 'Deskripsi',
            'aktif': 'Kategori Aktif',
        }


class FormProduk(forms.ModelForm):
    class Meta:
        model = Produk
        fields = [
            'kategori', 'nama_produk', 'deskripsi', 'bahan',
            'harga', 'stok', 'satuan', 'berat_gram',
            'foto', 'tersedia', 'unggulan',
        ]
        widgets = {
            'kategori': forms.Select(attrs={'class': 'form-control'}),
            'nama_produk': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nama produk...'}),
            'deskripsi': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Deskripsi produk...'}),
            'bahan': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Contoh: Tepung terigu, mentega, gula...'}),
            'harga': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0', 'min': '0', 'step': '500'}),
            'stok': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0', 'min': '0'}),
            'satuan': forms.Select(attrs={'class': 'form-control'}),
            'berat_gram': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Berat dalam gram (opsional)', 'min': '0'}),
            'foto': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'tersedia': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'unggulan': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'kategori': 'Kategori',
            'nama_produk': 'Nama Produk',
            'deskripsi': 'Deskripsi',
            'bahan': 'Bahan / Komposisi',
            'harga': 'Harga (Rp)',
            'stok': 'Stok',
            'satuan': 'Satuan',
            'berat_gram': 'Berat (gram)',
            'foto': 'Foto Produk',
            'tersedia': 'Produk Tersedia',
            'unggulan': 'Produk Unggulan',
        }

    def clean_harga(self):
        harga = self.cleaned_data.get('harga')
        if harga is not None and harga < 0:
            raise forms.ValidationError("Harga tidak boleh negatif.")
        return harga

    def clean_stok(self):
        stok = self.cleaned_data.get('stok')
        if stok is not None and stok < 0:
            raise forms.ValidationError("Stok tidak boleh negatif.")
        return stok

