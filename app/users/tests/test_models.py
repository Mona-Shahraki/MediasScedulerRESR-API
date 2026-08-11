from django.test import TestCase
from django.contrib.auth import get_user_model
from users.models import ConsultantProfile


class UserModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """Test creating a user with an email is successful."""
        email = 'test@example.com'
        password = 'testpass123'

        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test the email for a new user is normalized."""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.COM', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
        ]

        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(
                email=email,
                password='testpass123',
            )

            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test creating a user without an email raises a ValueError."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                email='',
                password='testpass123',
            )

    def test_create_superuser(self):
        """Test creating a superuser."""
        user = get_user_model().objects.create_superuser(
            email='admin@example.com',
            password='testpass123',
        )

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_user_password_is_not_plain_text(self):
        """Test that the password is not stored in plain text."""
        password = 'testpass123'

        user = get_user_model().objects.create_user(
            email='test@example.com',
            password=password,
        )

        self.assertNotEqual(user.password, password)
        self.assertTrue(user.check_password(password))

    def test_create_superuser_has_required_permissions(self):
        """Test that a superuser has the required permissions."""
        user = get_user_model().objects.create_superuser(
            email='admin@example.com',
            password='testpass123',
        )

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_active)

    def test_create_superuser_with_is_staff_false_raises_error(self):
        """Test that a superuser must have is_staff=True."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_superuser(
                email='admin@example.com',
                password='testpass123',
                is_staff=False,
            )

    def test_create_superuser_with_is_superuser_false_raises_error(self):
        """Test that a superuser must have is_superuser=True."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_superuser(
                email='admin@example.com',
                password='testpass123',
                is_superuser=False,
            )

    def test_create_consultant_profile(self):
        """Test creating a consultant profile."""
        user = get_user_model().objects.create_user(
            email='consultant@example.com',
            password='testpass123',
            name='Consultant One',
        )

        consultant = ConsultantProfile.objects.create(
            user=user,
            preferred_start_time='10:00',
        )

        self.assertEqual(consultant.user, user)
        self.assertEqual(
            consultant.preferred_start_time,
            '10:00',
        )