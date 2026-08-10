from django.test import TestCase
from django.core.exceptions import ValidationError
from rooms.models import Room


class RoomModelTests(TestCase):

    def test_create_room_successful(self):
        """Test creating a room is successful."""
        room = Room.objects.create(
            name='Room 1',
        )

        self.assertEqual(room.name, 'Room 1')

    def test_room_name_is_required(self):
        """Test that room name is required."""
        room = Room(name='')

        with self.assertRaises(ValidationError):
            room.full_clean()

    def test_room_string_representation(self):
        """Test the string representation of a room."""
        room = Room.objects.create(
            name='Room 1',
        )

        self.assertEqual(str(room), 'Room 1')

    def test_room_name_must_be_unique(self):
        """Test that room names must be unique."""
        Room.objects.create(
            name='Room 1',
        )

        duplicate_room = Room(
            name='Room 1',
        )

        with self.assertRaises(ValidationError):
            duplicate_room.full_clean()