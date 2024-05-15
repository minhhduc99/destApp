from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from manage_hotel.models import Room
from manage_hotel.serializers import RoomSerializer
from account.permissions import IsManager


class ListRoomView(APIView):
    def get(self, request):
        rooms = Room.objects.all()
        serializer = RoomSerializer(rooms, many=True)
        return Response({"data": serializer.data},
                        status=status.HTTP_200_OK)


class AddRoomView(APIView):
    permission_classes = [IsAuthenticated, IsManager]
    def post(self, request):
        room_number = request.data.get('room_number')
        room_type = request.data.get('room_type')
        room_price = request.data.get('room_price')
        room_description = request.data.get('room_description')

        data = {
            'room_number': room_number,
            'room_type': room_type,
            'room_price': room_price,
            'room_description': room_description
        }

        serializer = RoomSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":serializer.data},
                            status=status.HTTP_201_CREATED)
        return Response({"message": "Cannot add room"},
                        status=status.HTTP_400_BAD_REQUEST)


class EditRoomView(APIView):
    def get(self, request, pk):
        try:
            room = Room.objects.get(pk=pk)
        except Room.DoesNotExist:
            return Response({"message": "Cannot find this room"},
                            status=status.HTTP_404_NOT_FOUND)
        serializer = RoomSerializer(room)
        return Response({"data": serializer.data},
                        status=status.HTTP_200_OK)

    permission_classes = [IsAuthenticated, IsManager]
    def put(self, request, pk):
        try:
            room = Room.objects.get(pk=pk)
        except Room.DoesNotExist:
            return Response({"message": "Cannot find this room"},
                            status=status.HTTP_404_NOT_FOUND)
        room_number = request.data.get('room_number')
        room_type = request.data.get('room_type')
        room_price = request.data.get('room_price')
        room_description = request.data.get('room_description')

        data = {
            'room_number': room_number,
            'room_type': room_type,
            'room_price': room_price,
            'room_description': room_description
        }

        serializer = RoomSerializer(instance=room, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":serializer.data},
                            status=status.HTTP_200_OK)
        return Response({"message":"Cannot edit room"},
                        status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            room = Room.objects.get(pk=pk)
        except Room.DoesNotExist:
            return Response({"message": "Cannot find this room"},
                            status=status.HTTP_404_NOT_FOUND)
        room.delete()
        return Response({"message": "Delete Successfully"},
                        status=status.HTTP_200_OK)
