from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.hashers import make_password
from backend.models import User, Reservation, Installation
from datetime import date


class ReservationViewsTest(APITestCase):

    def setUp(self):
        # Crear usuarios para las pruebas
        self.user = User.objects.create(
            username='user1',
            first_name='Test User',
            password=make_password('userpassword')
        )
        self.other_user = User.objects.create(
            username='user2',
            first_name='Other User',
            password=make_password('otherpassword')
        )

        # Crear instalaciones para las pruebas
        self.installation1 = Installation.objects.create(
            name='Test Installation 1',
            capacity=10,
            roofed=True,
            area=50
        )
        self.installation2 = Installation.objects.create(
            name='Test Installation 2',
            capacity=20,
            roofed=False,
            area=100
        )

        # Crear reservas para las pruebas
        self.reservation = Reservation.objects.create(
            user=self.user,
            date=date.today(),
            installation=self.installation1
        )

    def authenticate_user(self, username, password):
        """Autenticar un usuario y configurar el token en el cliente"""
        response = self.client.post('/api/users/login/', {'username': username, 'password': password})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

    def test_get_all_reservations_authenticated(self):
        """Probar obtener todas las reservaciones para un usuario autenticado"""
        self.authenticate_user('user1', 'userpassword')
        response = self.client.get('/api/reservations/get/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['date'], str(date.today()))
        self.assertEqual(response.data[0]['installation'], self.installation1.name)

    def test_get_all_reservations_unauthenticated(self):
        """Probar que un usuario no autenticado no puede acceder a las reservas"""
        response = self.client.get('/api/reservations/get/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_add_reservation_authenticated(self):
        """Probar agregar una nueva reserva como usuario autenticado"""
        self.authenticate_user('user1', 'userpassword')
        data = {
            'date': str(date.today()),
            'installation_id': self.installation2.id
        }
        response = self.client.post('/api/reservations/add/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'Reserva agregada con éxito.')
        self.assertEqual(response.data['installation_id'], self.installation2.id)

    def test_add_reservation_duplicate(self):
        """Probar que no se puede agregar una reserva duplicada para la misma fecha e instalación"""
        self.authenticate_user('user1', 'userpassword')
        data = {
            'date': str(date.today()),
            'installation_id': self.installation1.id  # Usa la misma instalación definida en setUp
        }
        response = self.client.post('/api/reservations/add/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)  # Código de error esperado
        self.assertIn('non_field_errors', response.data)  # Verifica que el error está en non_field_errors
        self.assertEqual(
            response.data['non_field_errors'][0],
            "Esta instalación ya está reservada para esta fecha."  # Mensaje esperado
        )


    def test_add_reservation_unauthenticated(self):
        """Probar que un usuario no autenticado no puede agregar reservas"""
        data = {
            'date': str(date.today()),
            'installation_id': self.installation2.id
        }
        response = self.client.post('/api/reservations/add/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_add_reservation_invalid_data(self):
        """Probar que no se puede agregar una reserva con datos inválidos"""
        self.authenticate_user('user1', 'userpassword')
        data = {
            'date': '',  # Fecha inválida
            'installation_id': ''  # ID inválido
        }
        response = self.client.post('/api/reservations/add/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('date', response.data)
        self.assertIn('installation_id', response.data)
