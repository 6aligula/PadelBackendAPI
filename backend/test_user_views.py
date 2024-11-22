from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.hashers import make_password
from backend.models import User

class UserViewsTest(APITestCase):

    def setUp(self):
        # Crear usuarios para las pruebas
        self.admin_user = User.objects.create(
            username='admin',
            first_name='Admin',
            is_staff=True,
            password=make_password('adminpassword')
        )
        self.normal_user = User.objects.create(
            username='user1',
            first_name='User One',
            direccion='Address 1',
            telefono='1234567890',
            password=make_password('userpassword')
        )
        self.other_user = User.objects.create(
            username='user2',
            first_name='User Two',
            direccion='Address 2',
            telefono='0987654321',
            password=make_password('otherpassword')
        )

    def authenticate_user(self, username, password):
        response = self.client.post('/api/users/login/', {'username': username, 'password': password})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

    def test_register_user(self):
        data = {
            'nip': 'newuser',
            'name': 'New User',
            'direccion': 'New Address',
            'telefono': '1122334455',
            'password': 'newpassword'
        }
        response = self.client.post('/api/users/register/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], 'newuser')

    def test_login_user(self):
        data = {
            'username': 'user1',
            'password': 'userpassword'
        }
        response = self.client.post('/api/users/login/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['username'], 'user1')

    def test_get_user_profile(self):
        self.authenticate_user('user1', 'userpassword')
        response = self.client.get('/api/users/profile/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'user1')

    def test_update_user_profile(self):
        self.authenticate_user('user1', 'userpassword')
        data = {
            'name': 'Updated Name',
            'direccion': 'Updated Address',
            'telefono': '1112223333',
            'password': 'newpassword'
        }
        response = self.client.put('/api/users/profile/update/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.normal_user.refresh_from_db()
        self.assertEqual(self.normal_user.first_name, 'Updated Name')
        self.assertEqual(self.normal_user.direccion, 'Updated Address')
        self.assertTrue(self.normal_user.check_password('newpassword'))

    def test_get_users_as_admin(self):
        self.authenticate_user('admin', 'adminpassword')
        response = self.client.get('/api/users/all/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)  # 3 usuarios creados en setUp

    def test_get_users_as_non_admin(self):
        self.authenticate_user('user1', 'userpassword')
        response = self.client.get('/api/users/all/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_user_as_admin(self):
        self.authenticate_user('admin', 'adminpassword')
        data = {
            'name': 'Admin Updated User',
            'direccion': 'New Admin Address',
            'telefono': '9998887777',
            'isAdmin': True
        }
        response = self.client.put(f'/api/users/update/{self.normal_user.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.normal_user.refresh_from_db()
        self.assertEqual(self.normal_user.first_name, 'Admin Updated User')
        self.assertEqual(self.normal_user.direccion, 'New Admin Address')
        self.assertTrue(self.normal_user.is_staff)

    def test_update_user_without_permission(self):
        self.authenticate_user('user1', 'userpassword')
        data = {'name': 'Unauthorized Update'}
        response = self.client.put(f'/api/users/update/{self.other_user.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_user_as_admin(self):
        self.authenticate_user('admin', 'adminpassword')
        response = self.client.delete(f'/api/users/delete/{self.normal_user.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(User.objects.filter(id=self.normal_user.id).exists())

    def test_delete_user_self_not_allowed(self):
        self.authenticate_user('admin', 'adminpassword')
        response = self.client.delete(f'/api/users/delete/{self.admin_user.id}/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_user_without_permission(self):
        self.authenticate_user('user1', 'userpassword')
        response = self.client.delete(f'/api/users/delete/{self.other_user.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_access_profile_unauthenticated(self):
        response = self.client.get('/api/users/profile/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_register_user_existing_nip(self):
        data = {
            'nip': 'user1',  # NIP ya existente
            'name': 'Duplicate User',
            'direccion': 'Some Address',
            'telefono': '123456789',
            'password': 'somepassword'
        }
        response = self.client.post('/api/users/register/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('detail', response.data)

    def test_register_missing_fields(self):
        data = {
            'nip': '',
            'name': 'User',
            'direccion': 'Some Address',
            'telefono': '123456789',
            'password': 'password123'
        }
        response = self.client.post('/api/users/register/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('detail', response.data)

    def test_register_empty_fields(self):
        data = {
            'nip': '',
            'name': '',
            'direccion': '',
            'telefono': '',
            'password': ''
        }
        response = self.client.post('/api/users/register/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('detail', response.data)

    def test_register_with_optional_fields_empty(self):
        """Test de registro con todos los campos opcionales vacíos."""
        data = {
            'nip': 'validnip',
            'name': 'Valid Name',
            'direccion': 'Valid Address',
            'telefono': '1234567890',
            'password': 'ValidPassword'
        }
        response = self.client.post('/api/users/register/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
