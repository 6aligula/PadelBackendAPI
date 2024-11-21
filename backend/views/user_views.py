
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
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

    # Validar que todos los campos necesarios están presentes
    required_fields = ['nip', 'name', 'direccion', 'telefono', 'password']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return Response(
            {'detail': f'Faltan los siguientes campos: {", ".join(missing_fields)}'},
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
        print(f'Usuario registrado con éxito: {nip}.')
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Exception as e:
        # Capturar y registrar el error
        print(f'Error al registrar usuario: {str(e)}.')
        return Response(
            {'detail': 'Ocurrió un error al registrar el usuario.'},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getUserProfile(request):
    user = request.user
    serializer = UserSerializer(user, many=False)
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


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateUserProfile(request):
    user = request.user
    data = request.data

    # Actualiza el nombre, username/email y password si se proporcionan y no están vacíos
    update_attribute_if_provided(user, 'first_name', data.get('name'))
    email = data.get('email')
    if email:
        update_attribute_if_provided(user, 'username', email)
        update_attribute_if_provided(user, 'email', email)
    if 'password' in data and data['password']:
        user.password = make_password(data['password'])

    user.save()

    # Vuelve a generar el serializer para reflejar los cambios
    serializer = UserSerializerWithToken(user, many=False)
    return Response(serializer.data)
