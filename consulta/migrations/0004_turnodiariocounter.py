from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('consulta', '0003_turno_agendado_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='TurnoDiarioCounter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField(unique=True)),
                ('ultimo_numero', models.PositiveIntegerField(default=0)),
            ],
            options={
                'verbose_name': 'Contador diario de turnos',
                'verbose_name_plural': 'Contadores diarios de turnos',
            },
        ),
    ]
