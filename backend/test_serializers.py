from django.test import TestCase
from backend.models import User, Reservation, Installation
from backend.serializers import UserSerializer, UserSerializerWithToken, ReservationSerializer
from datetime import date


class SerializersTest(TestCase):

    def setUp(self):
        # Crear datos de prueba
        self.user = User.objects.create(
            username='testuser',
            first_name='Test',
            direccion='Test Address',
            telefono='123456789'
        )
        self.installation = Installation.objects.create(
            name='Test Installation',
            capacity=100,
            roofed=True,
            area=200
        )
        self.reservation = Reservation.objects.create(
            user=self.user,
            date=date.today(),
            installation=self.installation
        )

    def test_user_serializer(self):
        """Prueba el serializador de usuarios"""
        serializer = UserSerializer(self.user)
        data = serializer.data
        self.assertEqual(data['username'], 'testuser')
        self.assertEqual(data['direccion'], 'Test Address')
        self.assertEqual(data['telefono'], '123456789')

    def test_user_serializer_with_token(self):
        """Prueba el serializador de usuarios con token"""
        serializer = UserSerializerWithToken(self.user)
        data = serializer.data
        self.assertIn('token', data)
        self.assertEqual(data['username'], 'testuser')

    def test_reservation_serializer(self):
        """Prueba el serializador de reservas"""
        serializer = ReservationSerializer(self.reservation)
        data = serializer.data
        self.assertEqual(data['date'], str(date.today()))
        self.assertEqual(data['installation'], self.installation.name)

    def test_reservation_serializer_create(self):
        """Prueba la creación de reservas con el serializador"""
        data = {
            'date': str(date.today()),
            'installation_id': self.installation.id  # Usa la instalación definida en setUp
        }
        serializer = ReservationSerializer(data=data)
        self.assertFalse(serializer.is_valid())  # Esto debe fallar porque ya existe una reserva
        self.assertIn('non_field_errors', serializer.errors)  # El error debería estar aquí
        self.assertEqual(
            serializer.errors['non_field_errors'][0],
            "Esta instalación ya está reservada para esta fecha."
        )


    def test_reservation_serializer_invalid_installation(self):
        """Prueba de validación fallida en reservas con instalación inexistente"""
        data = {
            'date': str(date.today()),
            'installation_id': 999  # ID inexistente
        }
        serializer = ReservationSerializer(data=data)
        self.assertFalse(serializer.is_valid())  # Verifica que no sea válido
        self.assertIn('installation_id', serializer.errors)  # Confirma que el error está relacionado con installation_id

