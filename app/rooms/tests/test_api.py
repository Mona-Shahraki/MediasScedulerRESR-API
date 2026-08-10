from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from rooms.models import Room


class RoomApiTests(APITestCase):
    
    def create_user(self, **params):
            return get_user_model().objects.create_user(**params)

    def create_superuser(self):
        return get_user_model().objects.create_superuser(
            email='admin@example.com',
            password='testpass123',
            name='Admin',
        )

    def test_create_room_successful(self):
        """Test creating a room is successful."""
        user = self.create_superuser()
        self.client.force_authenticate(user)
        payload = {
            'name': 'Room 1',
        }

        response = self.client.post(
            reverse('room:list'),
            payload,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        room = Room.objects.get(id=response.data['id'])

        self.assertEqual(room.name, payload['name'])

    def test_create_room_with_duplicate_name(self):
        """Test creating a room with duplicate name fails."""
        user = self.create_superuser()
        self.client.force_authenticate(user)
        Room.objects.create(name='Room 1')

        payload = {
            'name': 'Room 1',
        }

        response = self.client.post(
            reverse('room:list'),
            payload,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_create_room_with_empty_name(self):
        """Test creating a room without a name fails."""
        user = self.create_superuser()
        self.client.force_authenticate(user)
        response = self.client.post(
            reverse('room:list'),
            {
                'name': '',
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_list_rooms(self):
        """Test retrieving a list of rooms."""
        user = self.create_superuser()
        self.client.force_authenticate(user)

        Room.objects.create(name='Room 1')
        Room.objects.create(name='Room 2')

        response = self.client.get(
            reverse('room:list'),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(len(response.data), 2)

    def test_retrieve_room(self):
        """Test retrieving a single room."""
        user = get_user_model().objects.create_user(
            email='user@example.com',
            password='testpass123',
            name='Normal User',
        )

        self.client.force_authenticate(user)

        room = Room.objects.create(
            name='Room 1',
        )

        response = self.client.get(
            reverse(
                'room:detail',
                args=[room.id],
            ),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data['id'],
            room.id,
        )

        self.assertEqual(
            response.data['name'],
            room.name,
        )
    def test_create_room_id_is_generated(self):
        """Test room ID is generated automatically."""
        user = self.create_superuser()
        self.client.force_authenticate(user)

        response = self.client.post(
            reverse('room:list'),
            {
                'id': 999,
                'name': 'Room 999',
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertNotEqual(
            response.data['id'],
            999,
        )

    def test_list_rooms_empty(self):
        """Test retrieving rooms when no rooms exist."""
        user = self.create_superuser()
        self.client.force_authenticate(user)

        response = self.client.get(
            reverse('room:list'),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data,
            [],
        )

    def test_create_room_requires_authentication(self):
        """Test that authentication is required to create a room."""
        response = self.client.post(
            reverse('room:list'),
            {
                'name': 'Room 1',
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_normal_user_cannot_create_room(self):
        """Test that a normal user cannot create a room."""
        user = get_user_model().objects.create_user(
            email='user@example.com',
            password='testpass123',
            name='Normal User',
        )

        self.client.force_authenticate(user)

        response = self.client.post(
            reverse('room:list'),
            {
                'name': 'Room 1',
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_superuser_can_create_room(self):
        """Test that a superuser can create a room."""
        user = get_user_model().objects.create_superuser(
            email='admin@example.com',
            password='testpass123',
            name='Admin',
        )

        self.client.force_authenticate(user)

        response = self.client.post(
            reverse('room:list'),
            {
                'name': 'Room 1',
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

    def test_update_room(self):
        """Test updating a room is successful."""
        user = self.create_superuser()
        self.client.force_authenticate(user)

        room = Room.objects.create(
            name='Room 1',
        )

        response = self.client.patch(
            reverse(
                'room:detail',
                args=[room.id],
            ),
            {
                'name': 'Updated Room',
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        room.refresh_from_db()

        self.assertEqual(
            room.name,
            'Updated Room',
        )

    def test_delete_room(self):
        """Test deleting a room is successful."""
        user = self.create_superuser()
        self.client.force_authenticate(user)

        room = Room.objects.create(
            name='Room 1',
        )

        response = self.client.delete(
            reverse(
                'room:detail',
                args=[room.id],
            ),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            Room.objects.filter(id=room.id).exists()
        )

    def test_normal_user_cannot_update_room(self):
        """Test normal users cannot update rooms."""
        user = get_user_model().objects.create_user(
            email='user@example.com',
            password='testpass123',
            name='Normal User',
        )

        self.client.force_authenticate(user)

        room = Room.objects.create(
            name='Room 1',
        )

        response = self.client.patch(
            reverse(
                'room:detail',
                args=[room.id],
            ),
            {
                'name': 'Updated Room',
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_normal_user_cannot_delete_room(self):
        """Test normal users cannot delete rooms."""
        user = get_user_model().objects.create_user(
            email='user@example.com',
            password='testpass123',
            name='Normal User',
        )

        self.client.force_authenticate(user)

        room = Room.objects.create(
            name='Room 1',
        )

        response = self.client.delete(
            reverse(
                'room:detail',
                args=[room.id],
            ),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
        
    def test_retrieve_room_requires_authentication(self):
        """Test authentication is required to retrieve a room."""
        room = Room.objects.create(
            name='Room 1',
        )

        response = self.client.get(
            reverse(
                'room:detail',
                args=[room.id],
            ),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )