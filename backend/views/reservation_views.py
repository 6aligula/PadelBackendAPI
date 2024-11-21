# reservation_views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from ..models import Reservation
from ..serializers import ReservationSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_reservation(request):
    # Filtrar las reservaciones del usuario autenticado
    reservations = Reservation.objects.filter(user=request.user)

    # Serializar las reservaciones
    serializer = ReservationSerializer(reservations, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_reservation(request):
    print("Datos recibidos en el POST: %s", request.data)
    # Asociar el usuario autenticado con la reserva
    data = request.data.copy()
    data['user'] = request.user.id  # Incluye el ID del usuario autenticado

    serializer = ReservationSerializer(data=data)
    if serializer.is_valid():
        print("Datos validados:", serializer.validated_data)
        # Verificar si ya existe una reserva para la misma fecha e instalación
        date = serializer.validated_data['date']
        installation_id = serializer.validated_data['installation_id']

        if Reservation.objects.filter(date=date, installation_id=installation_id).exists():
            return Response({'error': 'Esta instalación ya está reservada para esta fecha.'}, status=400)

        reservation = serializer.save(user=request.user)  # Guardar la reserva asociada al usuario
        return Response(
            {
                'id': reservation.id,
                'message': 'Reserva agregada con éxito.',
                'date': reservation.date,
                'installation_id': reservation.installation_id,
            },
            status=201
        )

    return Response(serializer.errors, status=400)