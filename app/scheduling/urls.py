from django.urls import path

from . import views

app_name = 'scheduling'

urlpatterns = [
    path(
        '',
        views.ScheduledSessionListCreateView.as_view(),
        name='session-list-create',
    ),
    path(
        '<int:pk>/',
        views.ScheduledSessionDetailView.as_view(),
        name='session-detail',
    ),
]