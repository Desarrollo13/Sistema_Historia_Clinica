from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from consulta.models import Turno
from facturacion.models import Pago
from pacientes.models import Paciente


class FacturacionFlowTests(TestCase):
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
            especialidad='Clinica medica',
        )
        self.paciente = Paciente.objects.create(
            dni='30444555',
            apellido='Suarez',
            nombre='Lucia',
            fecha_nacimiento='1995-09-12',
            sexo='F',
        )
        self.turno = Turno.objects.create(
            paciente=self.paciente,
            medico=self.medico,
            estado='finalizado',
        )
        self.client.force_login(self.recepcion)

    def test_registrar_pago_creates_pago_and_first_receipt_number(self):
        response = self.client.post(reverse('facturacion:registrar', args=[self.turno.pk]), {
            'concepto': 'Consulta Clinica medica',
            'monto': '15000.50',
            'forma_pago': 'efectivo',
            'observaciones': 'Pago total',
        })

        pago = Pago.objects.get()
        self.assertRedirects(response, reverse('facturacion:ticket', args=[pago.pk]))
        self.assertEqual(Pago.objects.count(), 1)
        self.assertEqual(pago.turno, self.turno)
        self.assertEqual(pago.nro_recibo, 1000)
        self.assertEqual(str(pago.monto), '15000.50')

    def test_medico_cannot_access_facturacion(self):
        self.client.force_login(self.medico)

        response = self.client.get(reverse('facturacion:lista'))

        self.assertRedirects(response, '/', fetch_redirect_response=False)
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any('No tienes permiso' in str(message) for message in messages))

    def test_no_se_puede_facturar_turno_no_finalizado(self):
        self.turno.estado = 'espera'
        self.turno.save(update_fields=['estado'])

        response = self.client.post(reverse('facturacion:registrar', args=[self.turno.pk]), {
            'concepto': 'Consulta Clinica medica',
            'monto': '15000.50',
            'forma_pago': 'efectivo',
        })

        self.assertRedirects(response, reverse('facturacion:lista'))
        self.assertEqual(Pago.objects.count(), 0)

    def test_receipt_numbers_are_sequential(self):
        otro_paciente = Paciente.objects.create(
            dni='30999877',
            apellido='Moyano',
            nombre='Elena',
            fecha_nacimiento='1991-03-20',
            sexo='F',
        )
        otro_turno = Turno.objects.create(
            paciente=otro_paciente,
            medico=self.medico,
            estado='finalizado',
        )

        primer_pago = Pago.objects.create(turno=self.turno, monto='1000', forma_pago='efectivo')
        segundo_pago = Pago.objects.create(turno=otro_turno, monto='2000', forma_pago='transferencia')

        self.assertEqual(primer_pago.nro_recibo, 1000)
        self.assertEqual(segundo_pago.nro_recibo, 1001)
