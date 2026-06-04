from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from consulta.models import Turno
from pacientes.models import Paciente, SignosVitales


class RecepcionIntakeTests(TestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.recepcion = self.user_model.objects.create_user(
            username='recepcion1',
            password='clave123',
            rol='recepcion',
        )
        self.medico = self.user_model.objects.create_user(
            username='medico1',
            password='clave123',
            rol='medico',
            first_name='Ana',
            last_name='Lopez',
        )
        self.paciente = Paciente.objects.create(
            dni='30111222',
            apellido='Perez',
            nombre='Juan',
            fecha_nacimiento='1990-05-10',
            sexo='M',
        )
        self.client.force_login(self.recepcion)

    def test_signos_vitales_creates_signs_and_turno(self):
        response = self.client.post(reverse('pacientes:signos_vitales', args=[self.paciente.pk]), {
            'presion_sistolica': '120',
            'presion_diastolica': '80',
            'frecuencia_cardiaca': '72',
            'temperatura': '36.6',
            'saturacion_o2': '98',
            'peso': '80.5',
            'talla': '180',
            'motivo_consulta': 'Control general',
            'observaciones': 'Sin novedades',
            'medico_id': str(self.medico.pk),
        })

        self.assertRedirects(response, reverse('pacientes:lista'))
        self.assertEqual(SignosVitales.objects.count(), 1)
        self.assertEqual(Turno.objects.count(), 1)

        signos = SignosVitales.objects.get()
        turno = Turno.objects.get()

        self.assertEqual(signos.paciente, self.paciente)
        self.assertEqual(signos.tomados_por, self.recepcion)
        self.assertEqual(turno.paciente, self.paciente)
        self.assertEqual(turno.signos, signos)
        self.assertEqual(turno.medico, self.medico)
        self.assertEqual(turno.estado, 'espera')
        self.assertEqual(turno.numero, 1)

    def test_agendar_turno_creates_scheduled_turn_with_channel(self):
        response = self.client.post(reverse('pacientes:agendar_turno', args=[self.paciente.pk]), {
            'fecha_hora': (timezone.localtime() + timedelta(days=1)).strftime('%Y-%m-%dT10:30'),
            'medico_id': str(self.medico.pk),
            'canal_solicitud': 'telefono',
            'motivo_turno': 'Control anual',
            'observaciones_recepcion': 'Solicitado por llamada',
        })

        self.assertRedirects(response, reverse('pacientes:detalle', args=[self.paciente.pk]))
        turno = Turno.objects.get()
        self.assertEqual(turno.estado, 'programado')
        self.assertEqual(turno.canal_solicitud, 'telefono')
        self.assertEqual(turno.motivo_turno, 'Control anual')
        self.assertEqual(turno.medico, self.medico)

    def test_agendar_turno_rejects_taken_slot_for_same_medico(self):
        fecha_hora = timezone.make_aware(datetime(2026, 6, 10, 10, 30), timezone.get_current_timezone())
        Turno.objects.create(
            paciente=self.paciente,
            medico=self.medico,
            estado='programado',
            fecha_hora=fecha_hora,
        )

        otro = Paciente.objects.create(
            dni='33444555',
            apellido='Ruiz',
            nombre='Laura',
            fecha_nacimiento='1992-04-12',
            sexo='F',
        )

        response = self.client.post(reverse('pacientes:agendar_turno', args=[otro.pk]), {
            'fecha_hora': fecha_hora.strftime('%Y-%m-%dT%H:%M'),
            'medico_id': str(self.medico.pk),
            'canal_solicitud': 'whatsapp',
            'motivo_turno': 'Consulta',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ya tiene un turno asignado')
        self.assertEqual(Turno.objects.count(), 1)

    def test_signos_vitales_reuses_scheduled_turn_for_today(self):
        fecha_hora = timezone.localtime() + timedelta(hours=2)
        turno = Turno.objects.create(
            paciente=self.paciente,
            medico=self.medico,
            estado='programado',
            canal_solicitud='whatsapp',
            motivo_turno='Dolor de garganta',
            fecha_hora=fecha_hora,
        )

        response = self.client.post(reverse('pacientes:signos_vitales', args=[self.paciente.pk]), {
            'presion_sistolica': '120',
            'presion_diastolica': '80',
            'motivo_consulta': 'Dolor de garganta',
            'observaciones': 'Paciente presente',
            'medico_id': str(self.medico.pk),
        })

        self.assertRedirects(response, reverse('pacientes:lista'))
        self.assertEqual(Turno.objects.count(), 1)
        turno.refresh_from_db()
        self.assertEqual(turno.estado, 'espera')
        self.assertIsNotNone(turno.signos)

    def test_editar_paciente_updates_data(self):
        response = self.client.post(reverse('pacientes:editar', args=[self.paciente.pk]), {
            'dni': '30111222',
            'apellido': 'Perez',
            'nombre': 'Juan Carlos',
            'fecha_nacimiento': '1990-05-10',
            'sexo': 'M',
            'telefono': '2615551234',
            'email': 'juan@example.com',
            'domicilio': 'San Martin 123',
            'ciudad': 'Mendoza',
            'grupo_sanguineo': 'O+',
            'obra_social': 'OSEP',
            'nro_afiliado': 'ABC123',
            'alergias': 'Ninguna',
            'antecedentes': 'Sin antecedentes',
            'medicacion_habitual': 'Ninguna',
        })

        self.assertRedirects(response, reverse('pacientes:detalle', args=[self.paciente.pk]))
        self.paciente.refresh_from_db()
        self.assertEqual(self.paciente.nombre, 'Juan Carlos')
        self.assertEqual(self.paciente.telefono, '2615551234')
        self.assertEqual(self.paciente.obra_social, 'OSEP')
        self.assertEqual(self.paciente.grupo_sanguineo, 'O+')

    def test_baja_paciente_marks_it_inactive(self):
        response = self.client.post(reverse('pacientes:baja', args=[self.paciente.pk]))

        self.assertRedirects(response, reverse('pacientes:lista'))
        self.paciente.refresh_from_db()
        self.assertFalse(self.paciente.activo)

    def test_lista_hides_inactive_patients(self):
        self.paciente.activo = False
        self.paciente.save(update_fields=['activo'])

        response = self.client.get(reverse('pacientes:lista'))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.paciente.nombre_completo)

    def test_inactive_list_shows_inactive_patients(self):
        self.paciente.activo = False
        self.paciente.save(update_fields=['activo'])

        response = self.client.get(reverse('pacientes:inactivos'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.paciente.nombre_completo)

    def test_reactivar_paciente_marks_it_active_again(self):
        self.paciente.activo = False
        self.paciente.save(update_fields=['activo'])

        response = self.client.post(reverse('pacientes:reactivar', args=[self.paciente.pk]))

        self.assertRedirects(response, reverse('pacientes:inactivos'))
        self.paciente.refresh_from_db()
        self.assertTrue(self.paciente.activo)
