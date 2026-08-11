from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from core.permissions import IsSuperUser

from .models import ConsultantProfile
from .serializers import UserSerializer, ConsultantSerializer, ConsultantCreateSerializer, UserProfileSerializer
from .serializers import (
    UserSerializer,
    ConsultantSerializer,
    ConsultantCreateSerializer,
)


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer


class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class ConsultantMeView(generics.RetrieveAPIView):
    serializer_class = ConsultantSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return ConsultantProfile.objects.get(
            user=self.request.user,
        )


class ConsultantCreateView(generics.CreateAPIView):
    serializer_class = ConsultantCreateSerializer
    permission_classes = [IsSuperUser]