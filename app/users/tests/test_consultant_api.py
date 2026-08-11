from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import ConsultantProfile


class ConsultantApiTests(APITestCase):

    def test_get_consultant_profile(self):
        """Test retrieving the authenticated consultant profile."""
        user = get_user_model().objects.create_user(
            email='consultant@example.com',
            password='testpass123',
            name='Consultant One',
        )

        ConsultantProfile.objects.create(
            user=user,
            preferred_start_time='10:00',
        )

        self.client.force_authenticate(user)

        response = self.client.get(
            reverse('user:consultant-me')
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data['name'],
            'Consultant One',
        )

        self.assertEqual(
            response.data['preferred_start_time'],
            '10:00:00',
        )

    def test_consultant_can_only_get_own_profile(self):
        """Test that a consultant only gets their own profile."""
        user = get_user_model().objects.create_user(
            email='consultant@example.com',
            password='testpass123',
            name='Consultant One',
        )

        ConsultantProfile.objects.create(
            user=user,
            preferred_start_time='10:00',
        )

        self.client.force_authenticate(user)

        response = self.client.get(
            reverse('user:consultant-me'),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data['name'],
            'Consultant One',
        )
    def test_consultant_profile_returns_preferred_start_time(self):
        """Test preferred start time is returned correctly."""
        user = get_user_model().objects.create_user(
            email='consultant@example.com',
            password='testpass123',
            name='Consultant One',
        )

        ConsultantProfile.objects.create(
            user=user,
            preferred_start_time='10:30',
        )

        self.client.force_authenticate(user)

        response = self.client.get(
            reverse('user:consultant-me'),
        )

        self.assertEqual(
            response.data['preferred_start_time'],
            '10:30:00',
        )

    def test_create_consultant_successful(self):
        """Test creating a consultant."""
        admin = get_user_model().objects.create_superuser(
            email='admin@example.com',
            password='testpass123',
            name='Admin',
        )

        self.client.force_authenticate(admin)

        payload = {
            'email': 'consultant@example.com',
            'password': 'testpass123',
            'name': 'Consultant One',
            'preferred_start_time': '10:00',
        }

        response = self.client.post(
            reverse('user:consultant-create'),
            payload,
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            get_user_model().objects.filter(
                email='consultant@example.com',
            ).exists(),
        )

        consultant = ConsultantProfile.objects.get(
            user__email='consultant@example.com',
        )

        self.assertEqual(
            consultant.preferred_start_time.strftime('%H:%M'),
            '10:00',
        )