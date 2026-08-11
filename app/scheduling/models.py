from django.core.exceptions import ValidationError
from django.db import models

from rooms.models import Room
from users.models import ConsultantProfile

class ScheduledSession(models.Model):
    SESSION_TYPE_EXAM = 'exam'
    SESSION_TYPE_CONSULTATION = 'consultation'

    SESSION_TYPE_CHOICES = [
        (SESSION_TYPE_EXAM, 'Exam'),
        (SESSION_TYPE_CONSULTATION, 'Consultation'),
    ]

    consultant = models.ForeignKey(
        ConsultantProfile,
        on_delete=models.CASCADE,
    )

    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
    )

    student_id = models.CharField(max_length=100)
    start_time = models.TimeField()
    end_time = models.TimeField()
    session_type = models.CharField(
        max_length=20,
        choices=SESSION_TYPE_CHOICES,
    )

    def clean(self):
        errors = {}

        if self.start_time and self.end_time:
            if self.end_time <= self.start_time:
                errors['end_time'] = 'End time must be after start time.'

        if self.consultant_id and self.start_time and self.end_time:
            consultant_conflict = ScheduledSession.objects.filter(
                consultant_id=self.consultant_id,
                start_time__lt=self.end_time,
                end_time__gt=self.start_time,
            ).exclude(pk=self.pk).exists()

            if consultant_conflict:
                errors['consultant'] = (
                    'Consultant already has a session during this time.'
                )

        if self.room_id and self.start_time and self.end_time:
            room_conflict = ScheduledSession.objects.filter(
                room_id=self.room_id,
                start_time__lt=self.end_time,
                end_time__gt=self.start_time,
            ).exclude(pk=self.pk).exists()

            if room_conflict:
                errors['room'] = (
                    'Room already has a session during this time.'
                )

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f'{self.student_id} - {self.session_type}'