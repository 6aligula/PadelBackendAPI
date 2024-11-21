from rest_framework import serializers
from backend.models import User, Reservation, Installation
from rest_framework_simplejwt.tokens import RefreshToken


class UserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(read_only=True)
    _id = serializers.SerializerMethodField(read_only=True)
    isAdmin = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ['id', '_id', 'username', 'email', 'direccion', 'telefono', 'name', 'isAdmin']

    def get__id(self, obj):
        return obj.id

    def get_isAdmin(self, obj):
        return obj.is_staff

    def get_name(self, obj):
        name = obj.first_name
        if name == '':
            name = obj.email
        return name

class UserSerializerWithToken(UserSerializer):
    token = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ['id', '_id', 'username', 'direccion', 'telefono', 'name', 'isAdmin', 'token']

    def get_token(self, obj):
        token = RefreshToken.for_user(obj)
        return str(token.access_token)

class ReservationSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)  # Muestra el username del usuario en lugar de su ID
    installation_id = serializers.PrimaryKeyRelatedField(
        queryset=Installation.objects.all(), write_only=True
    )  # Permite enviar `installation_id` desde el cliente
    installation = serializers.StringRelatedField(read_only=True)  # Muestra el nombre de la instalación en las respuestas

    class Meta:
        model = Reservation
        fields = ['id', 'user', 'date', 'installation_id', 'installation', 'is_synced', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'is_synced', 'created_at', 'updated_at']

    def create(self, validated_data):
        # Extrae el `installation_id` y lo convierte a una instancia del modelo `Installation`
        installation = validated_data.pop('installation_id')
        reservation = Reservation.objects.create(installation=installation, **validated_data)
        return reservation
