from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from consulta.models import HistoriaClinica, RecetaMedicamento, Turno
from pacientes.models import Paciente, SignosVitales


class ConsultaWorkflowTests(TestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.medico = self.user_model.objects.create_user(
            username='medico1',
            password='clave123',
            rol='medico',
            first_name='Ana',
            last_name='Lopez',
        )
        self.paciente = Paciente.objects.create(
            dni='30999888',
            apellido='Gomez',
            nombre='Maria',
            fecha_nacimiento='1988-02-20',
            sexo='F',
            alergias='Penicilina',
        )
        self.signos = SignosVitales.objects.create(
            paciente=self.paciente,
            tomados_por=self.medico,
            motivo_consulta='Dolor de cabeza',
            presion_sistolica=130,
            presion_diastolica=85,
        )
        self.turno = Turno.objects.create(
            paciente=self.paciente,
            signos=self.signos,
            medico=self.medico,
            estado='atencion',
        )
        self.client.force_login(self.medico)

    def test_nueva_historia_creates_historia_receta_and_finishes_turno(self):
        response = self.client.post(reverse('consulta:nueva_historia', args=[self.turno.pk]), {
            'anamnesis': 'Paciente con cefalea de 48 horas.',
            'examen_fisico': 'Buen estado general.',
            'diagnostico_principal': 'Cefalea tensional',
            'diagnosticos_secundarios': 'Sin hallazgos adicionales',
            'cie10': 'R51',
            'tratamiento': 'Analgesia y reposo.',
            'indicaciones': 'Control si empeora.',
            'proxima_consulta': '2026-06-10',
            'derivacion': 'Neurologia',
            'medicamento[]': ['Paracetamol'],
            'dosis[]': ['500 mg'],
            'forma[]': ['Comprimidos'],
            'posologia[]': ['1 cada 8 hs por 3 dias'],
        })

        self.assertRedirects(response, reverse('consulta:panel_medico'))
        self.assertEqual(HistoriaClinica.objects.count(), 1)
        self.assertEqual(RecetaMedicamento.objects.count(), 1)

        self.turno.refresh_from_db()
        historia = HistoriaClinica.objects.get()
        receta = RecetaMedicamento.objects.get()

        self.assertEqual(self.turno.estado, 'finalizado')
        self.assertIsNotNone(self.turno.hora_fin)
        self.assertEqual(historia.turno, self.turno)
        self.assertEqual(historia.medico, self.medico)
        self.assertEqual(historia.diagnostico_principal, 'Cefalea tensional')
        self.assertEqual(receta.historia, historia)
        self.assertEqual(receta.medicamento, 'Paracetamol')

    def test_receta_pdf_returns_pdf_response(self):
        historia = HistoriaClinica.objects.create(
            turno=self.turno,
            medico=self.medico,
            anamnesis='Texto',
            examen_fisico='Texto',
            diagnostico_principal='Diagnostico',
            tratamiento='Tratamiento',
        )

        response = self.client.get(reverse('consulta:receta_pdf', args=[historia.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn(f'receta_{historia.pk}.pdf', response['Content-Disposition'])
