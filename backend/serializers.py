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

    def validate(self, attrs):
        installation_id = attrs.get('installation_id')
        date = attrs.get('date')

        # Verificar si la instalación existe
        if not Installation.objects.filter(id=installation_id).exists():
            raise serializers.ValidationError({"installation_id": "Instalación no encontrada."})

        # Verificar duplicidad de reserva
        if Reservation.objects.filter(date=date, installation_id=installation_id).exists():
            raise serializers.ValidationError({
                "non_field_errors": "Esta instalación ya está reservada para esta fecha."
            })

        return attrs

    def create(self, validated_data):
        installation_id = validated_data.pop('installation_id')
        installation = Installation.objects.get(id=installation_id)
        return Reservation.objects.create(installation=installation, **validated_data)


