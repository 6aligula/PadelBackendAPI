
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from backend.models import User
from django.contrib.auth.hashers import make_password
from backend.serializers import UserSerializer, UserSerializerWithToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from rest_framework.exceptions import AuthenticationFailed



class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        try:
            data = super().validate(attrs)

            serializer = UserSerializerWithToken(self.user).data

            for k, v in serializer.items():
                data[k] = v

            username = self.user.username
            print(f'Inicio de sesión exitoso para el usuario: {username}')
            return data
        except AuthenticationFailed:
            print('Intento de inicio de sesión fallido')
            raise
            

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

@api_view(['POST'])
def registerUser(request):
    data = request.data

    # Validar que los campos obligatorios estén presentes y no estén vacíos
    required_fields = ['nip', 'name', 'direccion', 'telefono', 'password']
    missing_or_empty_fields = [field for field in required_fields if not data.get(field)]
    if missing_or_empty_fields:
        return Response(
            {'detail': f'Faltan los siguientes campos: {", ".join(missing_or_empty_fields)}'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Asignar y limpiar datos
    nip = data['nip'].strip().lower()
    name = data['name'].strip()
    direccion = data['direccion'].strip()
    telefono = data['telefono'].strip()
    password = data['password'].strip()

    # Verificar si el NIP (username) ya existe
    if User.objects.filter(username=nip).exists():
        return Response(
            {'detail': 'El NIP ya está en uso. Por favor, elige otro.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Intentar crear el usuario
    try:
        user = User.objects.create(
            first_name=name,
            username=nip,  # Usamos el NIP como username
            direccion=direccion,
            telefono=telefono,
            password=make_password(password)
        )
        serializer = UserSerializerWithToken(user, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response(
            {'detail': f'Ocurrió un error al registrar el usuario: {str(e)}'},
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getUserProfile(request):
    user = request.user
    serializer = UserSerializer(user, many=False)
    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateUser(request, pk):
    try:
        user = User.objects.get(id=pk)
    except User.DoesNotExist:
        return Response({'detail': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    # Solo un admin o el propio usuario puede actualizar datos
    if not (request.user.is_staff or request.user.id == user.id):
        return Response({'detail': 'No tienes permiso para actualizar este usuario.'}, status=status.HTTP_403_FORBIDDEN)

    data = request.data

    # Actualizar solo los campos proporcionados
    update_attribute_if_provided(user, 'first_name', data.get('name', None))
    update_attribute_if_provided(user, 'direccion', data.get('direccion', None))
    update_attribute_if_provided(user, 'telefono', data.get('telefono', None))
    if request.user.is_staff:
        update_attribute_if_provided(user, 'is_staff', data.get('isAdmin', None))

    # Actualizar la contraseña si es proporcionada y no vacía
    if data.get('password') and data['password'].strip() != '':
        user.password = make_password(data['password'].strip())

    user.save()

    serializer = UserSerializer(user, many=False)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateUserProfile(request):
    user = request.user
    data = request.data

    # Actualizar solo los campos proporcionados
    update_attribute_if_provided(user, 'first_name', data.get('name', None))
    update_attribute_if_provided(user, 'direccion', data.get('direccion', None))
    update_attribute_if_provided(user, 'telefono', data.get('telefono', None))

    # Actualizar la contraseña si es proporcionada y no vacía
    if data.get('password') and data['password'].strip() != '':
        user.password = make_password(data['password'].strip())

    user.save()

    serializer = UserSerializer(user, many=False)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def deleteUser(request, pk):
    try:
        user = User.objects.get(id=pk)
    except User.DoesNotExist:
        return Response({'detail': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    # No permitir que el administrador se elimine a sí mismo
    if request.user.id == user.id:
        return Response({'detail': 'No puedes eliminar tu propia cuenta.'}, status=status.HTTP_400_BAD_REQUEST)

    user.delete()
    return Response({'detail': 'Usuario eliminado con éxito.'}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def getUsers(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)

def update_attribute_if_provided(instance, attribute, value):
    """
    Actualiza un atributo de una instancia si el valor proporcionado no está vacío.
    
    :param instance: La instancia a actualizar.
    :param attribute: El nombre del atributo a actualizar.
    :param value: El valor nuevo para el atributo.
    """
    if value is not None and value != '':
        setattr(instance, attribute, value)

