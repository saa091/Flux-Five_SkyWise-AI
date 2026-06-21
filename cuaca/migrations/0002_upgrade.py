from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ('cuaca', '0001_initial'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        # Add warna to Kategori
        migrations.AddField(
            model_name='kategori',
            name='warna',
            field=models.CharField(
                choices=[('blue','Biru'),('green','Hijau'),('yellow','Kuning'),
                         ('red','Merah'),('purple','Ungu'),('gray','Abu'),
                         ('cyan','Cyan'),('orange','Oranye')],
                default='blue', max_length=20),
        ),
        # Upgrade Galeri
        migrations.AddField(model_name='galeri', name='kota',
            field=models.CharField(default='', max_length=100)),
        migrations.AddField(model_name='galeri', name='kondisi_cuaca',
            field=models.CharField(
                choices=[('cerah','☀️ Cerah'),('berawan','⛅ Berawan'),('hujan','🌧️ Hujan'),
                         ('badai','⛈️ Badai'),('berkabut','🌫️ Berkabut'),('salju','❄️ Salju'),
                         ('angin','💨 Angin Kencang'),('lainnya','🌈 Lainnya')],
                default='lainnya', max_length=20)),
        migrations.AddField(model_name='galeri', name='nama_pengunggah',
            field=models.CharField(blank=True, max_length=100,
                                   help_text='Diisi otomatis jika tidak login')),
        migrations.AddField(model_name='galeri', name='disetujui',
            field=models.BooleanField(default=False)),
        migrations.AlterField(model_name='galeri', name='kategori',
            field=models.ForeignKey(blank=True, null=True,
                                    on_delete=django.db.models.deletion.SET_NULL,
                                    to='cuaca.kategori')),
        migrations.AlterField(model_name='galeri', name='diunggah_oleh',
            field=models.ForeignKey(blank=True, null=True,
                                    on_delete=django.db.models.deletion.SET_NULL,
                                    to='auth.user')),
        # FavoritKota
        migrations.CreateModel(
            name='FavoritKota',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nama_kota', models.CharField(max_length=100)),
                ('negara', models.CharField(blank=True, max_length=10)),
                ('dibuat', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                           related_name='favorit_kota', to='auth.user')),
            ],
            options={'verbose_name_plural': 'Favorit Kota', 'ordering': ['-dibuat'],
                     'unique_together': {('user', 'nama_kota')}},
        ),
    ]
