from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('facturacion', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReciboCounter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('clave', models.CharField(default='global', max_length=20, unique=True)),
                ('ultimo_numero', models.PositiveIntegerField(default=999)),
            ],
            options={
                'verbose_name': 'Contador de recibos',
                'verbose_name_plural': 'Contadores de recibos',
            },
        ),
    ]
