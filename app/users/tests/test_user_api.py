from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.core.exceptions import ValidationError
from users.models import User, ConsultantProfile


class UserApiTests(APITestCase):

    def test_create_user_success(self):
        """Test creating a user is successful."""
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test User',
        }

        response = self.client.post(
            reverse('user:create'),
            payload,
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = get_user_model().objects.get(
            email=payload['email'],
        )

        self.assertTrue(user.check_password(payload['password']))
        self.assertEqual(user.name, payload['name'])

        self.assertNotIn('password', response.data)

    def test_user_with_existing_email(self):
        """Test creating a user with an email that already exists."""
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test User',
        }

        get_user_model().objects.create_user(**payload)

        response = self.client.post(
            reverse('user:create'),
            payload,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_password_too_short(self):
        """Test creating a user with a password less than 8 characters."""
        payload = {
            'email': 'test@example.com',
            'password': '123',
            'name': 'Test User',
        }

        response = self.client.post(
            reverse('user:create'),
            payload,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertFalse(
            get_user_model().objects.filter(
                email=payload['email'],
            ).exists()
        )

    def test_email_required(self):
        """Test email is required."""
        payload = {
            'password': 'testpass123',
            'name': 'Test User',
        }

        response = self.client.post(
            reverse('user:create'),
            payload,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_password_required(self):
        """Test password is required."""
        payload = {
            'email': 'test@example.com',
            'name': 'Test User',
        }

        response = self.client.post(
            reverse('user:create'),
            payload,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_invalid_email(self):
        """Test invalid email cannot be used."""
        payload = {
            'email': 'not-an-email',
            'password': 'testpass123',
            'name': 'Test User',
        }

        response = self.client.post(
            reverse('user:create'),
            payload,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_password_not_returned(self):
        """Test password is never returned in the response."""
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test User',
        }

        response = self.client.post(
            reverse('user:create'),
            payload,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertNotIn('password', response.data)

    def test_create_token_for_user(self):
        """Test generating token is successful."""
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
        }

        get_user_model().objects.create_user(**payload)

        response = self.client.post(
            reverse('user:token'),
            payload,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_create_token_with_invalid_credentials(self):
        """Test token is not generated with invalid credentials."""
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
        }

        get_user_model().objects.create_user(**payload)

        response = self.client.post(
            reverse('user:token'),
            {
                'email': payload['email'],
                'password': 'wrongpass123',
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

        self.assertNotIn('access', response.data)
        self.assertNotIn('refresh', response.data)

    def test_create_token_with_unknown_email(self):
        """Test token is not generated for an unknown email."""
        response = self.client.post(
            reverse('user:token'),
            {
                'email': 'unknown@example.com',
                'password': 'testpass123',
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

        self.assertNotIn('access', response.data)
        self.assertNotIn('refresh', response.data)

    def test_retrieve_user_unauthenticated(self):
        """Test authentication is required to retrieve user."""
        response = self.client.get(
            reverse('user:me'),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_retrieve_profile_success(self):
        """Test retrieving profile for authenticated user."""
        user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpass123',
            name='Test User',
        )

        self.client.force_authenticate(user)

        response = self.client.get(
            reverse('user:me'),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(response.data, {
            'email': user.email,
            'name': user.name,
        })

    def test_user_can_only_have_one_consultant_profile(self):
        """Test a user can only have one consultant profile."""
        user = get_user_model().objects.create_user(
            email='consultant@example.com',
            password='testpass123',
            name='Consultant One',
        )

        ConsultantProfile.objects.create(
            user=user,
            preferred_start_time='10:00',
        )

        with self.assertRaises(Exception):
            ConsultantProfile.objects.create(
                user=user,
                preferred_start_time='11:00',
            )

    def test_consultant_profile_string_representation(self):
        """Test the string representation of a consultant profile."""
        user = get_user_model().objects.create_user(
            email='consultant@example.com',
            password='testpass123',
            name='Consultant One',
        )

        consultant = ConsultantProfile.objects.create(
            user=user,
            preferred_start_time='10:00',
        )

        self.assertEqual(
            str(consultant),
            'Consultant One',
        )

    def test_preferred_start_time_is_required(self):
        """Test preferred start time is required."""
        user = get_user_model().objects.create_user(
            email='consultant@example.com',
            password='testpass123',
            name='Consultant One',
        )

        consultant = ConsultantProfile(
            user=user,
            preferred_start_time=None,
        )

        with self.assertRaises(ValidationError):
            consultant.full_clean()