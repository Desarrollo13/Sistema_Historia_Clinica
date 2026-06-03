from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

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
