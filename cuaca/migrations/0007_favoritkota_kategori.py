from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cuaca', '0006_alter_favoritkota_unique_together_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='favoritkota',
            name='kategori',
            field=models.CharField(default='Kota', max_length=30),
        ),
    ]