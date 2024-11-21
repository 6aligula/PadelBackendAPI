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
    user = serializers.SerializerMethodField(read_only=True)  # Devuelve el username del usuario
    installation_id = serializers.IntegerField(write_only=True)  # Cambia a IntegerField
    installation = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Reservation
        fields = ['id', 'user', 'date', 'installation_id', 'installation', 'is_synced', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'is_synced', 'created_at', 'updated_at']
    
    def get_user(self, obj):
        return obj.user.first_name  # O devuelve obj.user.first_name si prefieres el primer nombre

    def create(self, validated_data):
        installation_id = validated_data.pop('installation_id')  # Extrae el ID como entero
        try:
            installation = Installation.objects.get(id=installation_id)  # Busca el objeto
        except Installation.DoesNotExist:
            raise serializers.ValidationError({"installation_id": "Instalación no encontrada."})

        # Crea la reserva con el objeto `installation` y los datos validados
        reservation = Reservation.objects.create(installation=installation, **validated_data)
        return reservation




