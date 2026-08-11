from datetime import time

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from rooms.models import Room
from scheduling.models import ScheduledSession
from users.models import ConsultantProfile


class ScheduledSessionModelTests(TestCase):

    def create_consultant(self):
        user = get_user_model().objects.create_user(
            email='consultant@example.com',
            password='testpass123',
        )
        return ConsultantProfile.objects.create(
            user=user,
            preferred_start_time=time(8, 0),
        )

    def create_session(self, **params):
        consultant = params.pop('consultant', None)

        if consultant is None:
            consultant = self.create_consultant()

        room = params.pop('room', None)

        if room is None:
            room = Room.objects.create(name='Room 1')

        defaults = {
            'consultant': consultant,
            'room': room,
            'student_id': 'student-001',
            'start_time': time(10, 0),
            'end_time': time(11, 0),
            'session_type': 'exam',
        }

        defaults.update(params)

        return ScheduledSession.objects.create(**defaults)

    def test_create_scheduled_session_successful(self):
        """Test creating a scheduled session is successful."""
        session = self.create_session()

        self.assertEqual(session.student_id, 'student-001')
        self.assertEqual(session.start_time, time(10, 0))
        self.assertEqual(session.end_time, time(11, 0))
        self.assertEqual(session.session_type, 'exam')

    def test_end_time_must_be_after_start_time(self):
        """Test that end time must be after start time."""
        session = ScheduledSession(
            student_id='student-001',
            start_time=time(11, 0),
            end_time=time(10, 0),
            session_type='exam',
        )

        with self.assertRaises(ValidationError):
            session.full_clean()

    def test_session_type_must_be_valid(self):
        """Test that session type must be a valid choice."""
        session = ScheduledSession(
            student_id='student-001',
            start_time=time(10, 0),
            end_time=time(11, 0),
            session_type='invalid',
        )

        with self.assertRaises(ValidationError):
            session.full_clean()

    def test_create_scheduled_session_with_consultant(self):
        """Test creating a session with a consultant."""
        consultant = self.create_consultant()

        session = self.create_session(
            consultant=consultant,
        )

        self.assertEqual(session.consultant, consultant)

    def test_create_scheduled_session_with_room(self):
        """Test creating a session with a room."""
        room = Room.objects.create(name='Room 1')

        session = self.create_session(
            room=room,
        )

        self.assertEqual(session.room, room)

    def test_consultant_is_required(self):
        """Test that consultant is required."""
        room = Room.objects.create(name='Room 1')

        session = ScheduledSession(
            room=room,
            student_id='student-001',
            start_time=time(10, 0),
            end_time=time(11, 0),
            session_type='exam',
        )

        with self.assertRaises(ValidationError):
            session.full_clean()

    def test_room_is_required(self):
        """Test that room is required."""
        consultant = self.create_consultant()

        session = ScheduledSession(
            consultant=consultant,
            student_id='student-001',
            start_time=time(10, 0),
            end_time=time(11, 0),
            session_type='exam',
        )

        with self.assertRaises(ValidationError):
            session.full_clean()

    def test_consultant_cannot_have_overlapping_sessions(self):
        """Test that a consultant cannot have overlapping sessions."""
        consultant = self.create_consultant()
        room1 = Room.objects.create(name='Room 1')
        room2 = Room.objects.create(name='Room 2')

        self.create_session(
            consultant=consultant,
            room=room1,
            start_time=time(10, 0),
            end_time=time(11, 0),
        )

        session = ScheduledSession(
            consultant=consultant,
            room=room2,
            student_id='student-002',
            start_time=time(10, 30),
            end_time=time(11, 30),
            session_type='consultation',
        )

        with self.assertRaises(ValidationError):
            session.full_clean()

    def test_room_cannot_have_overlapping_sessions(self):
        """Test that a room cannot have overlapping sessions."""
        consultant1 = self.create_consultant()

        user = get_user_model().objects.create_user(
            email='consultant2@example.com',
            password='testpass123',
        )
        consultant2 = ConsultantProfile.objects.create(
            user=user,
            preferred_start_time=time(8, 0),
        )

        room = Room.objects.create(name='Room 1')

        self.create_session(
            consultant=consultant1,
            room=room,
            start_time=time(10, 0),
            end_time=time(11, 0),
        )

        session = ScheduledSession(
            consultant=consultant2,
            room=room,
            student_id='student-002',
            start_time=time(10, 30),
            end_time=time(11, 30),
            session_type='consultation',
        )

        with self.assertRaises(ValidationError):
            session.full_clean()

    def test_session_can_start_when_another_session_ends(self):
        """Test sessions can be back-to-back."""
        consultant = self.create_consultant()
        room1 = Room.objects.create(name='Room 1')
        room2 = Room.objects.create(name='Room 2')

        self.create_session(
            consultant=consultant,
            room=room1,
            start_time=time(10, 0),
            end_time=time(11, 0),
        )

        session = self.create_session(
            consultant=consultant,
            room=room2,
            start_time=time(11, 0),
            end_time=time(12, 0),
        )

        self.assertEqual(session.start_time, time(11, 0))

    def test_session_can_end_when_another_session_starts(self):
        """Test sessions can end when another session starts."""
        consultant = self.create_consultant()
        room1 = Room.objects.create(name='Room 1')
        room2 = Room.objects.create(name='Room 2')

        self.create_session(
            consultant=consultant,
            room=room1,
            start_time=time(11, 0),
            end_time=time(12, 0),
        )

        session = self.create_session(
            consultant=consultant,
            room=room2,
            start_time=time(10, 0),
            end_time=time(11, 0),
        )

        self.assertEqual(session.end_time, time(11, 0))

    def test_consultant_cannot_have_session_inside_another(self):
        """Test a session cannot be inside another session."""
        consultant = self.create_consultant()
        room1 = Room.objects.create(name='Room 1')
        room2 = Room.objects.create(name='Room 2')

        self.create_session(
            consultant=consultant,
            room=room1,
            start_time=time(10, 0),
            end_time=time(12, 0),
        )

        session = ScheduledSession(
            consultant=consultant,
            room=room2,
            student_id='student-002',
            start_time=time(10, 30),
            end_time=time(11, 30),
            session_type='consultation',
        )

        with self.assertRaises(ValidationError):
            session.full_clean()