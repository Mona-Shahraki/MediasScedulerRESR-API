from django.urls import path

from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
)


app_name = 'user'

urlpatterns = [
    path(
        'create/',
        views.CreateUserView.as_view(),
        name='create',
    ),
    path(
        'token/',
        TokenObtainPairView.as_view(),
        name='token',
    ),
    path(
        'me/',
        views.ManageUserView.as_view(),
        name='me',
    ),
]