from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cuaca', '0007_favoritkota_kategori'),
    ]

    operations = [
        migrations.DeleteModel(
            name='FavoritKota',
        ),
    ]