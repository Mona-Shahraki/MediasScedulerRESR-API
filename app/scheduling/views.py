from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import ScheduledSession
from .serializers import ScheduledSessionSerializer


class ScheduledSessionListCreateView(generics.ListCreateAPIView):
    queryset = ScheduledSession.objects.all()
    serializer_class = ScheduledSessionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ScheduledSession.objects.filter(
            consultant__user=self.request.user
        )

class ScheduledSessionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ScheduledSession.objects.all()
    serializer_class = ScheduledSessionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ScheduledSession.objects.filter(
            consultant__user=self.request.user
        )
