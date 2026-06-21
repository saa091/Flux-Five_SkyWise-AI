from django.db import migrations

KATEGORI_DEFAULT = [
    ('Cerah',        '☀️', 'yellow',
     'Cuaca cerah dengan sinar matahari penuh. Langit biru dan tidak ada awan.'),
    ('Berawan',      '⛅', 'blue',
     'Langit tertutup sebagian atau seluruhnya oleh awan. Suhu relatif normal.'),
    ('Hujan',        '🌧️', 'cyan',
     'Curah hujan dari ringan hingga lebat. Pastikan membawa payung.'),
    ('Badai',        '⛈️', 'purple',
     'Cuaca ekstrem dengan petir, kilat, dan angin kencang. Tetap di dalam ruangan.'),
    ('Berkabut',     '🌫️', 'gray',
     'Visibilitas rendah akibat kabut tebal. Berkendara dengan hati-hati.'),
    ('Angin Kencang','💨', 'orange',
     'Hembusan angin dengan kecepatan tinggi. Amankan benda-benda ringan.'),
]

def seed_kategori(apps, schema_editor):
    Kategori = apps.get_model('cuaca', 'Kategori')
    if Kategori.objects.count() == 0:
        for nama, icon, warna, deskripsi in KATEGORI_DEFAULT:
            Kategori.objects.create(nama=nama, icon=icon, warna=warna, deskripsi=deskripsi)

class Migration(migrations.Migration):
    dependencies = [('cuaca', '0002_upgrade')]
    operations   = [migrations.RunPython(seed_kategori, migrations.RunPython.noop)]
