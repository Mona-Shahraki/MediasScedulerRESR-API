from django.urls import path

from . import views


app_name = 'room'

urlpatterns = [
    path(
        '',
        views.RoomListCreateView.as_view(),
        name='list',
    ),
    path(
        '<int:pk>/',
        views.RoomDetailView.as_view(),
        name='detail',
    ),
]