from django.test import TestCase
from backend.models import User, Installation, Reservation
from datetime import date


class ModelsTest(TestCase):

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

    def test_user_model_str(self):
        """Prueba la representación en string del modelo User"""
        self.assertEqual(str(self.user), 'testuser')

    def test_installation_model_str(self):
        """Prueba la representación en string del modelo Installation"""
        self.assertEqual(str(self.installation), 'Test Installation')

    def test_reservation_model_str(self):
        """Prueba la representación en string del modelo Reservation"""
        reservation = Reservation.objects.create(
            user=self.user,
            date=date.today(),
            installation=self.installation
        )
        expected_str = f"Reservation by {self.user.username} on {reservation.date} for {self.installation.name}"
        self.assertEqual(str(reservation), expected_str)

    def test_reservation_unique_together(self):
        """Prueba que no se pueden crear dos reservas con la misma fecha e instalación"""
        Reservation.objects.create(
            user=self.user,
            date=date.today(),
            installation=self.installation
        )
        with self.assertRaises(Exception):
            Reservation.objects.create(
                user=self.user,
                date=date.today(),
                installation=self.installation
            )
