from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class LoginViewTests(TestCase):
    def setUp(self):
        self.user_model = get_user_model()

    def test_medico_login_redirects_to_panel(self):
        medico = self.user_model.objects.create_user(
            username='medico1',
            password='clave123',
            rol='medico',
        )

        response = self.client.post(reverse('cuentas:login'), {
            'username': medico.username,
            'password': 'clave123',
        })

        self.assertRedirects(response, '/consulta/panel/')

    def test_recepcion_login_redirects_to_patients(self):
        recepcion = self.user_model.objects.create_user(
            username='recepcion1',
            password='clave123',
            rol='recepcion',
        )

        response = self.client.post(reverse('cuentas:login'), {
            'username': recepcion.username,
            'password': 'clave123',
        })

        self.assertRedirects(response, '/pacientes/')

    def test_logout_redirects_to_login_without_template(self):
        user = self.user_model.objects.create_user(
            username='usuario1',
            password='clave123',
            rol='recepcion',
        )
        self.client.force_login(user)

        response = self.client.get(reverse('cuentas:logout'))

        self.assertRedirects(response, reverse('cuentas:login'))


class ConfiguracionViewsTests(TestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.admin = self.user_model.objects.create_user(
            username='admin1',
            password='clave123',
            rol='admin',
            first_name='Ada',
        )
        self.recepcion = self.user_model.objects.create_user(
            username='recepcion1',
            password='clave123',
            rol='recepcion',
        )

    def test_admin_can_access_configuracion(self):
        self.client.force_login(self.admin)

        response = self.client.get(reverse('cuentas:configuracion'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Gestionar usuarios')
        self.assertContains(response, 'Gestionar medicos')

    def test_recepcion_cannot_access_configuracion(self):
        self.client.force_login(self.recepcion)

        response = self.client.get(reverse('cuentas:configuracion'))

        self.assertRedirects(response, '/', fetch_redirect_response=False)

    def test_admin_can_create_medico_from_simple_form(self):
        self.client.force_login(self.admin)

        response = self.client.post(reverse('cuentas:nuevo_medico'), {
            'username': 'medico2',
            'first_name': 'Ana',
            'last_name': 'Lopez',
            'email': 'ana@example.com',
            'telefono': '2615550000',
            'especialidad': 'Clinica medica',
            'matricula': 'MAT-100',
            'password': 'clave123',
            'is_active': 'on',
        })

        self.assertRedirects(response, reverse('cuentas:lista_medicos'))
        medico = self.user_model.objects.get(username='medico2')
        self.assertEqual(medico.rol, 'medico')
        self.assertEqual(medico.especialidad, 'Clinica medica')
        self.assertTrue(medico.check_password('clave123'))
