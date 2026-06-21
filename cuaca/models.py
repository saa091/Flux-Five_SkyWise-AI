from django.db import models
from django.contrib.auth.models import User

class Kategori(models.Model):
    WARNA_CHOICES = [
        ('blue','Biru'), ('green','Hijau'), ('yellow','Kuning'),
        ('red','Merah'), ('purple','Ungu'), ('gray','Abu'),
        ('cyan','Cyan'), ('orange','Oranye'),
    ]
    nama      = models.CharField(max_length=100)
    deskripsi = models.TextField(blank=True)
    icon      = models.CharField(max_length=10, default='🌤️')
    warna     = models.CharField(max_length=20, choices=WARNA_CHOICES, default='blue')

    def __str__(self):
        return self.nama

    class Meta:
        verbose_name_plural = 'Kategori'

class TipsCuaca(models.Model):
    judul    = models.CharField(max_length=200)
    isi      = models.TextField()
    kategori = models.ForeignKey(Kategori, on_delete=models.CASCADE)
    gambar   = models.ImageField(upload_to='tips/', blank=True, null=True)
    penulis  = models.ForeignKey(User, on_delete=models.CASCADE)
    dibuat   = models.DateTimeField(auto_now_add=True)
    diupdate = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.judul

    class Meta:
        verbose_name_plural = 'Tips Cuaca'

class Galeri(models.Model):
    KONDISI_CHOICES = [
        ('cerah',    '☀️ Cerah'),
        ('berawan',  '⛅ Berawan'),
        ('hujan',    '🌧️ Hujan'),
        ('badai',    '⛈️ Badai'),
        ('berkabut', '🌫️ Berkabut'),
        ('salju',    '❄️ Salju'),
        ('angin',    '💨 Angin Kencang'),
        ('lainnya',  '🌈 Lainnya'),
    ]
    judul           = models.CharField(max_length=200)
    gambar          = models.ImageField(upload_to='galeri/')
    deskripsi       = models.TextField(blank=True)
    kota            = models.CharField(max_length=100, default='')
    kondisi_cuaca   = models.CharField(max_length=20, choices=KONDISI_CHOICES, default='lainnya')
    kategori        = models.ForeignKey(Kategori, on_delete=models.SET_NULL, null=True, blank=True)
    diunggah_oleh   = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    nama_pengunggah = models.CharField(max_length=100, blank=True, help_text='Diisi otomatis jika tidak login')
    disetujui       = models.BooleanField(default=False)
    dibuat          = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.judul

    @property
    def pengunggah_display(self):
        if self.diunggah_oleh:
            return self.diunggah_oleh.get_full_name() or self.diunggah_oleh.username
        return self.nama_pengunggah or 'Anonim'

    class Meta:
        verbose_name_plural = 'Galeri'
        ordering = ['-dibuat']

class Feedback(models.Model):
    RATING_CHOICES = [(i, i) for i in range(1, 6)]
    PENGALAMAN_CHOICES = [
        ('Sangat Puas', '🚀 Sangat Puas'),
        ('Puas',        '😊 Puas'),
        ('Cukup',       '😐 Cukup'),
        ('Tidak Puas',  '😞 Tidak Puas'),
    ]
    nama          = models.CharField(max_length=100)
    pesan         = models.TextField()
    rating        = models.IntegerField(choices=RATING_CHOICES)
    pengalaman    = models.CharField(max_length=50, choices=PENGALAMAN_CHOICES)
    balasan_admin = models.TextField(blank=True, null=True)
    dibuat        = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nama} - {self.rating}★"

    class Meta:
        verbose_name_plural = 'Feedback'