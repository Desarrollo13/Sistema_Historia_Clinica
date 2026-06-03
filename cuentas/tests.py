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
