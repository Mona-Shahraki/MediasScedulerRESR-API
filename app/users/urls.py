from django.urls import path

from rest_framework_simplejwt.views import TokenObtainPairView

from . import views


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
    path(
        'consultant/me/',
        views.ConsultantMeView.as_view(),
        name='consultant-me',
    ),
    path(
        'consultant/create/',
        views.ConsultantCreateView.as_view(),
        name='consultant-create',
    ),
]