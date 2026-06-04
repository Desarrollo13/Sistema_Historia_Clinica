from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('consulta', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='turno',
            name='canal_solicitud',
            field=models.CharField(choices=[('telefono', 'Telefono'), ('presencial', 'Presencial'), ('whatsapp', 'WhatsApp')], default='presencial', max_length=15),
        ),
        migrations.AddField(
            model_name='turno',
            name='motivo_turno',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='turno',
            name='observaciones_recepcion',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='turno',
            name='estado',
            field=models.CharField(choices=[('programado', 'Programado'), ('espera', 'En espera'), ('llamado', 'Llamado'), ('atencion', 'En atención'), ('finalizado', 'Finalizado'), ('cancelado', 'Cancelado')], default='espera', max_length=15),
        ),
    ]
