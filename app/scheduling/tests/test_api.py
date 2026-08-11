from datetime import time

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from rooms.models import Room
from users.models import ConsultantProfile
from scheduling.models import ScheduledSession


class ScheduledSessionApiTests(APITestCase):

    def create_consultant(self):
        user = get_user_model().objects.create_user(
            email='consultant@example.com',
            password='testpass123',
        )

        return ConsultantProfile.objects.create(
            user=user,
            preferred_start_time=time(8, 0),
        )

    def setUp(self):
        self.client.force_authenticate(
            user=get_user_model().objects.create_user(
                email='user@example.com',
                password='testpass123',
            )
        )

    def test_create_scheduled_session_successful(self):
        """Test creating a scheduled session is successful."""
        consultant = self.create_consultant()
        self.client.force_authenticate(user=consultant.user)
        room = Room.objects.create(name='Room 1')

        payload = {
            'consultant': consultant.id,
            'room': room.id,
            'student_id': 'student-001',
            'start_time': '10:00:00',
            'end_time': '11:00:00',
            'session_type': 'exam',
        }

        response = self.client.post(
            '/api/scheduling/',
            payload,
            format='json',
        )

        self.assertEqual(response.status_code, 201)

        session = ScheduledSession.objects.get(
            id=response.data['id']
        )

        self.assertEqual(session.consultant, consultant)
        self.assertEqual(session.room, room)
        self.assertEqual(session.student_id, 'student-001')

    def test_create_scheduled_session_requires_authentication(self):
        """Test creating a session requires authentication."""
        self.client.force_authenticate(user=None)

        consultant = self.create_consultant()
        room = Room.objects.create(name='Room 1')

        payload = {
            'consultant': consultant.id,
            'room': room.id,
            'student_id': 'student-001',
            'start_time': '10:00:00',
            'end_time': '11:00:00',
            'session_type': 'exam',
        }

        response = self.client.post(
            '/api/scheduling/',
            payload,
            format='json',
        )

        self.assertEqual(response.status_code, 401)

    def test_create_scheduled_session_without_consultant(self):
        """Test creating a session without a consultant fails."""
        room = Room.objects.create(name='Room 1')

        payload = {
            'room': room.id,
            'student_id': 'student-001',
            'start_time': '10:00:00',
            'end_time': '11:00:00',
            'session_type': 'exam',
        }

        response = self.client.post(
            '/api/scheduling/',
            payload,
            format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('consultant', response.data)

    def test_create_scheduled_session_without_room(self):
        """Test creating a session without a room fails."""
        consultant = self.create_consultant()

        payload = {
            'consultant': consultant.id,
            'student_id': 'student-001',
            'start_time': '10:00:00',
            'end_time': '11:00:00',
            'session_type': 'exam',
        }

        response = self.client.post(
            '/api/scheduling/',
            payload,
            format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('room', response.data)

    def test_create_scheduled_session_with_invalid_time_range(self):
        """Test end time must be after start time."""
        consultant = self.create_consultant()
        room = Room.objects.create(name='Room 1')

        payload = {
            'consultant': consultant.id,
            'room': room.id,
            'student_id': 'student-001',
            'start_time': '11:00:00',
            'end_time': '10:00:00',
            'session_type': 'exam',
        }

        response = self.client.post(
            '/api/scheduling/',
            payload,
            format='json',
        )

        self.assertEqual(response.status_code, 400)

    def test_create_scheduled_session_with_overlapping_consultant(self):
        """Test consultant cannot have overlapping sessions."""
        consultant = self.create_consultant()
        room1 = Room.objects.create(name='Room 1')
        room2 = Room.objects.create(name='Room 2')

        ScheduledSession.objects.create(
            consultant=consultant,
            room=room1,
            student_id='student-001',
            start_time='10:00:00',
            end_time='11:00:00',
            session_type='exam',
        )

        payload = {
            'consultant': consultant.id,
            'room': room2.id,
            'student_id': 'student-002',
            'start_time': '10:30:00',
            'end_time': '11:30:00',
            'session_type': 'consultation',
        }

        response = self.client.post(
            '/api/scheduling/',
            payload,
            format='json',
        )

        self.assertEqual(response.status_code, 400)

    def test_create_scheduled_session_with_overlapping_room(self):
        """Test room cannot have overlapping sessions."""
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
        room2 = Room.objects.create(name='Room 2')

        ScheduledSession.objects.create(
            consultant=consultant1,
            room=room,
            student_id='student-001',
            start_time='10:00:00',
            end_time='11:00:00',
            session_type='exam',
        )

        payload = {
            'consultant': consultant2.id,
            'room': room.id,
            'student_id': 'student-002',
            'start_time': '10:30:00',
            'end_time': '11:30:00',
            'session_type': 'consultation',
        }

        response = self.client.post(
            '/api/scheduling/',
            payload,
            format='json',
        )

        self.assertEqual(response.status_code, 400)

    def test_list_scheduled_sessions(self):
        """Test listing scheduled sessions."""
        user = get_user_model().objects.create_user(
            email='list-consultant@example.com',
            password='testpass123',
        )

        consultant = ConsultantProfile.objects.create(
            user=user,
            preferred_start_time=time(8, 0),
        )

        self.client.force_authenticate(user=user)

        room = Room.objects.create(name='Room 1')

        ScheduledSession.objects.create(
            consultant=consultant,
            room=room,
            student_id='student-001',
            start_time='10:00:00',
            end_time='11:00:00',
            session_type='exam',
        )

        ScheduledSession.objects.create(
            consultant=consultant,
            room=room,
            student_id='student-002',
            start_time='12:00:00',
            end_time='13:00:00',
            session_type='consultation',
        )

        response = self.client.get(
            '/api/scheduling/',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)


    def test_retrieve_scheduled_session(self):
        """Test retrieving a scheduled session."""
        consultant = self.create_consultant()
        self.client.force_authenticate(user=consultant.user)
        room = Room.objects.create(name='Room 1')

        session = ScheduledSession.objects.create(
            consultant=consultant,
            room=room,
            student_id='student-001',
            start_time='10:00:00',
            end_time='11:00:00',
            session_type='exam',
        )

        response = self.client.get(
            f'/api/scheduling/{session.id}/',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], session.id)
        self.assertEqual(
            response.data['student_id'],
            'student-001',
        )

    def test_retrieve_scheduled_session_requires_authentication(self):
        """Test retrieving a scheduled session requires authentication."""
        consultant = self.create_consultant()
        room = Room.objects.create(name='Room 1')

        session = ScheduledSession.objects.create(
            consultant=consultant,
            room=room,
            student_id='student-001',
            start_time='10:00:00',
            end_time='11:00:00',
            session_type='exam',
        )

        self.client.force_authenticate(user=None)

        response = self.client.get(
            f'/api/scheduling/{session.id}/',
        )

        self.assertEqual(response.status_code, 401)

    def test_update_scheduled_session_successful(self):
        """Test an authenticated user can update a scheduled session."""
        consultant = self.create_consultant()
        self.client.force_authenticate(user=consultant.user)
        room = Room.objects.create(name='Room 1')

        session = ScheduledSession.objects.create(
            consultant=consultant,
            room=room,
            student_id='student-001',
            start_time='10:00:00',
            end_time='11:00:00',
            session_type='exam',
        )

        payload = {
            'consultant': consultant.id,
            'room': room.id,
            'student_id': 'student-002',
            'start_time': '12:00:00',
            'end_time': '13:00:00',
            'session_type': 'consultation',
        }

        response = self.client.put(
            f'/api/scheduling/{session.id}/',
            payload,
            format='json',
        )

        self.assertEqual(response.status_code, 200)

        session.refresh_from_db()

        self.assertEqual(session.student_id, 'student-002')
        self.assertEqual(
            session.session_type,
            'consultation',
        )
        self.assertEqual(
            session.start_time.strftime('%H:%M:%S'),
            '12:00:00',
        )

    def test_update_scheduled_session_with_invalid_time_range(self):
        """Test updating a session with an invalid time range."""
        consultant = self.create_consultant()
        self.client.force_authenticate(user=consultant.user)
        room = Room.objects.create(name='Room 1')

        session = ScheduledSession.objects.create(
            consultant=consultant,
            room=room,
            student_id='student-001',
            start_time='10:00:00',
            end_time='11:00:00',
            session_type='exam',
        )

        payload = {
            'consultant': consultant.id,
            'room': room.id,
            'student_id': 'student-001',
            'start_time': '14:00:00',
            'end_time': '13:00:00',
            'session_type': 'exam',
        }

        response = self.client.put(
            f'/api/scheduling/{session.id}/',
            payload,
            format='json',
        )

        self.assertEqual(response.status_code, 400)

    def test_update_scheduled_session_with_overlapping_consultant(self):
        """Test updating a session to overlap another consultant session."""
        consultant = self.create_consultant()
        self.client.force_authenticate(user=consultant.user)
        room = Room.objects.create(name='Room 1')
        room2 = Room.objects.create(name='Room 2')

        ScheduledSession.objects.create(
            consultant=consultant,
            room=room,
            student_id='student-001',
            start_time='10:00:00',
            end_time='11:00:00',
            session_type='exam',
        )

        session = ScheduledSession.objects.create(
            consultant=consultant,
            room=room2,
            student_id='student-002',
            start_time='12:00:00',
            end_time='13:00:00',
            session_type='exam',
        )

        payload = {
            'consultant': consultant.id,
            'room': room2.id,
            'student_id': 'student-002',
            'start_time': '10:30:00',
            'end_time': '11:30:00',
            'session_type': 'exam',
        }

        response = self.client.put(
            f'/api/scheduling/{session.id}/',
            payload,
            format='json',
        )

        self.assertEqual(response.status_code, 400)

    def test_update_scheduled_session_with_overlapping_room(self):
        """Test updating a session to overlap another room session."""
        consultant = self.create_consultant()
        self.client.force_authenticate(user=consultant.user)

        room = Room.objects.create(name='Room 1')
        room2 = Room.objects.create(name='Room 2')

        ScheduledSession.objects.create(
            consultant=consultant,
            room=room,
            student_id='student-001',
            start_time='10:00:00',
            end_time='11:00:00',
            session_type='exam',
        )

        session = ScheduledSession.objects.create(
            consultant=consultant,
            room=room2,
            student_id='student-002',
            start_time='12:00:00',
            end_time='13:00:00',
            session_type='exam',
        )

        payload = {
            'consultant': consultant.id,
            'room': room.id,
            'student_id': 'student-002',
            'start_time': '10:30:00',
            'end_time': '11:30:00',
            'session_type': 'exam',
        }

        response = self.client.put(
            f'/api/scheduling/{session.id}/',
            payload,
            format='json',
        )

        self.assertEqual(response.status_code, 400)

    def test_update_scheduled_session_requires_authentication(self):
        """Test updating a scheduled session requires authentication."""
        consultant = self.create_consultant()
        self.client.force_authenticate(user=consultant.user)
        room = Room.objects.create(name='Room 1')

        session = ScheduledSession.objects.create(
            consultant=consultant,
            room=room,
            student_id='student-001',
            start_time='10:00:00',
            end_time='11:00:00',
            session_type='exam',
        )

        self.client.force_authenticate(user=None)

        payload = {
            'consultant': consultant.id,
            'room': room.id,
            'student_id': 'student-002',
            'start_time': '12:00:00',
            'end_time': '13:00:00',
            'session_type': 'consultation',
        }

        response = self.client.put(
            f'/api/scheduling/{session.id}/',
            payload,
            format='json',
        )

        self.assertEqual(response.status_code, 401)

    def test_delete_scheduled_session_successful(self):
        """Test an authenticated user can delete a scheduled session."""
        consultant = self.create_consultant()
        self.client.force_authenticate(user=consultant.user)
        room = Room.objects.create(name='Room 1')

        session = ScheduledSession.objects.create(
            consultant=consultant,
            room=room,
            student_id='student-001',
            start_time='10:00:00',
            end_time='11:00:00',
            session_type='exam',
        )

        response = self.client.delete(
            f'/api/scheduling/{session.id}/',
        )

        self.assertEqual(response.status_code, 204)
        self.assertFalse(
            ScheduledSession.objects.filter(id=session.id).exists()
        )

    def test_delete_scheduled_session_requires_authentication(self):
        """Test deleting a scheduled session requires authentication."""
        consultant = self.create_consultant()
        room = Room.objects.create(name='Room 1')

        session = ScheduledSession.objects.create(
            consultant=consultant,
            room=room,
            student_id='student-001',
            start_time='10:00:00',
            end_time='11:00:00',
            session_type='exam',
        )

        self.client.force_authenticate(user=None)

        response = self.client.delete(
            f'/api/scheduling/{session.id}/',
        )

        self.assertEqual(response.status_code, 401)

    def test_partial_update_scheduled_session_successful(self):
        """Test a scheduled session can be partially updated."""
        consultant = self.create_consultant()
        self.client.force_authenticate(user=consultant.user)
        room = Room.objects.create(name='Room 1')

        session = ScheduledSession.objects.create(
            consultant=consultant,
            room=room,
            student_id='student-001',
            start_time='10:00:00',
            end_time='11:00:00',
            session_type='exam',
        )

        payload = {
            'session_type': 'consultation',
        }

        response = self.client.patch(
            f'/api/scheduling/{session.id}/',
            payload,
            format='json',
        )

        self.assertEqual(response.status_code, 200)

        session.refresh_from_db()

        self.assertEqual(session.session_type, 'consultation')
        self.assertEqual(session.student_id, 'student-001')
        self.assertEqual(session.start_time.strftime('%H:%M:%S'), '10:00:00')
        self.assertEqual(session.end_time.strftime('%H:%M:%S'), '11:00:00')
        self.assertEqual(session.consultant, consultant)
        self.assertEqual(session.room, room)

    def test_partial_update_scheduled_session_with_overlapping_consultant(self):
        """Test PATCH prevents consultant schedule overlap."""
        consultant = self.create_consultant()
        self.client.force_authenticate(user=consultant.user)

        room1 = Room.objects.create(name='Room 1')
        room2 = Room.objects.create(name='Room 2')

        ScheduledSession.objects.create(
            consultant=consultant,
            room=room1,
            student_id='student-001',
            start_time='10:00:00',
            end_time='11:00:00',
            session_type='exam',
        )

        session = ScheduledSession.objects.create(
            consultant=consultant,
            room=room2,
            student_id='student-002',
            start_time='12:00:00',
            end_time='13:00:00',
            session_type='exam',
        )

        payload = {
            'start_time': '10:30:00',
            'end_time': '11:30:00',
        }

        response = self.client.patch(
            f'/api/scheduling/{session.id}/',
            payload,
            format='json',
        )

        self.assertEqual(response.status_code, 400)

    def test_partial_update_scheduled_session_with_overlapping_room(self):
        """Test PATCH prevents room schedule overlap."""
        consultant = self.create_consultant()
        self.client.force_authenticate(user=consultant.user)

        room1 = Room.objects.create(name='Room 1')
        room2 = Room.objects.create(name='Room 2')

        ScheduledSession.objects.create(
            consultant=consultant,
            room=room1,
            student_id='student-001',
            start_time='10:00:00',
            end_time='11:00:00',
            session_type='exam',
        )

        session = ScheduledSession.objects.create(
            consultant=consultant,
            room=room2,
            student_id='student-002',
            start_time='12:00:00',
            end_time='13:00:00',
            session_type='exam',
        )

        payload = {
            'room': room1.id,
            'start_time': '10:30:00',
            'end_time': '11:30:00',
        }

        response = self.client.patch(
            f'/api/scheduling/{session.id}/',
            payload,
            format='json',
        )

        self.assertEqual(response.status_code, 400)

    def test_list_scheduled_sessions_only_returns_current_consultants_sessions(self):
        """Test consultant only sees their own scheduled sessions."""
        user1 = get_user_model().objects.create_user(
            email='consultant1@example.com',
            password='testpass123',
        )
        consultant1 = ConsultantProfile.objects.create(
            user=user1,
            preferred_start_time=time(8, 0),
        )

        user2 = get_user_model().objects.create_user(
            email='consultant2@example.com',
            password='testpass123',
        )
        consultant2 = ConsultantProfile.objects.create(
            user=user2,
            preferred_start_time=time(8, 0),
        )

        room = Room.objects.create(name='Room 1')

        own_session = ScheduledSession.objects.create(
            consultant=consultant1,
            room=room,
            student_id='student-001',
            start_time='10:00:00',
            end_time='11:00:00',
            session_type='exam',
        )

        other_session = ScheduledSession.objects.create(
            consultant=consultant2,
            room=room,
            student_id='student-002',
            start_time='12:00:00',
            end_time='13:00:00',
            session_type='exam',
        )

        self.client.force_authenticate(user=user1)

        response = self.client.get('/api/scheduling/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], own_session.id)
        self.assertNotEqual(response.data[0]['id'], other_session.id)

    def test_retrieve_scheduled_session_of_another_consultant_returns_404(self):
        """Test consultant cannot retrieve another consultant's session."""
        user1 = get_user_model().objects.create_user(
            email='consultant1@example.com',
            password='testpass123',
        )
        consultant1 = ConsultantProfile.objects.create(
            user=user1,
            preferred_start_time=time(8, 0),
        )

        user2 = get_user_model().objects.create_user(
            email='consultant2@example.com',
            password='testpass123',
        )
        consultant2 = ConsultantProfile.objects.create(
            user=user2,
            preferred_start_time=time(8, 0),
        )

        room = Room.objects.create(name='Room 1')

        session = ScheduledSession.objects.create(
            consultant=consultant2,
            room=room,
            student_id='student-001',
            start_time='10:00:00',
            end_time='11:00:00',
            session_type='exam',
        )

        self.client.force_authenticate(user=user1)

        response = self.client.get(
            f'/api/scheduling/{session.id}/',
        )

        self.assertEqual(response.status_code, 404)

    def test_update_scheduled_session_of_another_consultant_returns_404(self):
        """Test consultant cannot update another consultant's session."""
        user1 = get_user_model().objects.create_user(
            email='consultant1@example.com',
            password='testpass123',
        )
        consultant1 = ConsultantProfile.objects.create(
            user=user1,
            preferred_start_time=time(8, 0),
        )

        user2 = get_user_model().objects.create_user(
            email='consultant2@example.com',
            password='testpass123',
        )
        consultant2 = ConsultantProfile.objects.create(
            user=user2,
            preferred_start_time=time(8, 0),
        )

        room = Room.objects.create(name='Room 1')

        session = ScheduledSession.objects.create(
            consultant=consultant2,
            room=room,
            student_id='student-001',
            start_time='10:00:00',
            end_time='11:00:00',
            session_type='exam',
        )

        self.client.force_authenticate(user=user1)

        payload = {
            'consultant': consultant2.id,
            'room': room.id,
            'student_id': 'student-updated',
            'start_time': '12:00:00',
            'end_time': '13:00:00',
            'session_type': 'consultation',
        }

        response = self.client.put(
            f'/api/scheduling/{session.id}/',
            payload,
            format='json',
        )

        self.assertEqual(response.status_code, 404)

        session.refresh_from_db()
        self.assertEqual(session.student_id, 'student-001')

    def test_partial_update_scheduled_session_of_another_consultant_returns_404(self):
        """Test consultant cannot partially update another consultant's session."""
        user1 = get_user_model().objects.create_user(
            email='consultant1@example.com',
            password='testpass123',
        )
        consultant1 = ConsultantProfile.objects.create(
            user=user1,
            preferred_start_time=time(8, 0),
        )

        user2 = get_user_model().objects.create_user(
            email='consultant2@example.com',
            password='testpass123',
        )
        consultant2 = ConsultantProfile.objects.create(
            user=user2,
            preferred_start_time=time(8, 0),
        )

        room = Room.objects.create(name='Room 1')

        session = ScheduledSession.objects.create(
            consultant=consultant2,
            room=room,
            student_id='student-001',
            start_time='10:00:00',
            end_time='11:00:00',
            session_type='exam',
        )

        self.client.force_authenticate(user=user1)

        payload = {
            'student_id': 'student-updated',
        }

        response = self.client.patch(
            f'/api/scheduling/{session.id}/',
            payload,
            format='json',
        )

        self.assertEqual(response.status_code, 404)

        session.refresh_from_db()
        self.assertEqual(session.student_id, 'student-001')

    def test_delete_scheduled_session_of_another_consultant_returns_404(self):
        """Test consultant cannot delete another consultant's session."""
        user1 = get_user_model().objects.create_user(
            email='consultant1@example.com',
            password='testpass123',
        )
        consultant1 = ConsultantProfile.objects.create(
            user=user1,
            preferred_start_time=time(8, 0),
        )

        user2 = get_user_model().objects.create_user(
            email='consultant2@example.com',
            password='testpass123',
        )
        consultant2 = ConsultantProfile.objects.create(
            user=user2,
            preferred_start_time=time(8, 0),
        )

        room = Room.objects.create(name='Room 1')

        session = ScheduledSession.objects.create(
            consultant=consultant2,
            room=room,
            student_id='student-001',
            start_time='10:00:00',
            end_time='11:00:00',
            session_type='exam',
        )

        self.client.force_authenticate(user=user1)

        response = self.client.delete(
            f'/api/scheduling/{session.id}/',
        )

        self.assertEqual(response.status_code, 404)

        self.assertTrue(
            ScheduledSession.objects.filter(id=session.id).exists()
        )

    def test_create_scheduled_session_for_another_consultant_returns_400(self):
        """Test consultant cannot create a session for another consultant."""
        user1 = get_user_model().objects.create_user(
            email='consultant1@example.com',
            password='testpass123',
        )
        consultant1 = ConsultantProfile.objects.create(
            user=user1,
            preferred_start_time=time(8, 0),
        )

        user2 = get_user_model().objects.create_user(
            email='consultant2@example.com',
            password='testpass123',
        )
        consultant2 = ConsultantProfile.objects.create(
            user=user2,
            preferred_start_time=time(8, 0),
        )

        room = Room.objects.create(name='Room 1')

        self.client.force_authenticate(user=user1)

        payload = {
            'consultant': consultant2.id,
            'room': room.id,
            'student_id': 'student-001',
            'start_time': '10:00:00',
            'end_time': '11:00:00',
            'session_type': 'exam',
        }

        response = self.client.post(
            '/api/scheduling/',
            payload,
            format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            ScheduledSession.objects.count(),
            0,
        )