from rest_framework import generics

from core.permissions import IsSuperUser

from .models import Room
from .serializers import RoomSerializer
from rest_framework.permissions import IsAuthenticated


class RoomListCreateView(generics.ListCreateAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [IsSuperUser]


class RoomDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]

        return [IsSuperUser()]