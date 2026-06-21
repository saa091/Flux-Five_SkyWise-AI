from django.contrib import admin
from .models import Kategori, TipsCuaca, Feedback, Galeri

@admin.register(Kategori)
class KategoriAdmin(admin.ModelAdmin):
    list_display = ('icon', 'nama', 'warna')
    search_fields = ('nama',)

@admin.register(TipsCuaca)
class TipsCuacaAdmin(admin.ModelAdmin):
    list_display = ('judul', 'kategori', 'penulis', 'dibuat')
    list_filter = ('kategori',)
    search_fields = ('judul',)

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('nama', 'rating', 'pengalaman', 'dibuat')
    list_filter = ('rating',)

@admin.register(Galeri)
class GaleriAdmin(admin.ModelAdmin):
    list_display = ('judul', 'kota', 'kondisi_cuaca', 'disetujui', 'diunggah_oleh', 'dibuat')
    list_filter = ('disetujui', 'kondisi_cuaca')
    list_editable = ('disetujui',)
    search_fields = ('judul', 'kota')
    actions = ['approve_photos', 'reject_photos']

    def approve_photos(self, request, queryset):
        queryset.update(disetujui=True)
        self.message_user(request, f'{queryset.count()} foto disetujui.')
    approve_photos.short_description = '✅ Setujui foto terpilih'

    def reject_photos(self, request, queryset):
        queryset.delete()
        self.message_user(request, 'Foto ditolak dan dihapus.')
    reject_photos.short_description = '❌ Tolak & hapus foto terpilih'