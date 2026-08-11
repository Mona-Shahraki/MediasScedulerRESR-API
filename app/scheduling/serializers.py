from rest_framework import serializers

from .models import ScheduledSession


class ScheduledSessionSerializer(serializers.ModelSerializer):

    class Meta:
        model = ScheduledSession
        fields = [
            'id',
            'consultant',
            'room',
            'student_id',
            'start_time',
            'end_time',
            'session_type',
        ]
        read_only_fields = ['id']

    def validate(self, attrs):
        start_time = attrs.get(
            'start_time',
            self.instance.start_time if self.instance else None,
        )
        end_time = attrs.get(
            'end_time',
            self.instance.end_time if self.instance else None,
        )
        consultant = attrs.get(
            'consultant',
            self.instance.consultant if self.instance else None,
        )
        room = attrs.get(
            'room',
            self.instance.room if self.instance else None,
        )

        request = self.context.get('request')

        if request and request.user.is_authenticated:
            if consultant and consultant.user != request.user:
                raise serializers.ValidationError(
                    'You can only create a session for yourself.'
                )

        # Validate time range
        if start_time and end_time and end_time <= start_time:
            raise serializers.ValidationError(
                'End time must be after start time.'
            )

    # ...
        # Validate consultant overlap
        if consultant and start_time and end_time:
            consultant_conflict = ScheduledSession.objects.filter(
                consultant=consultant,
                start_time__lt=end_time,
                end_time__gt=start_time,
            ).exclude(
                pk=self.instance.pk if self.instance else None
            ).exists()

            if consultant_conflict:
                raise serializers.ValidationError(
                    'Consultant already has a session during this time.'
                )

        # Validate room overlap
        if room and start_time and end_time:
            room_conflict = ScheduledSession.objects.filter(
                room=room,
                start_time__lt=end_time,
                end_time__gt=start_time,
            ).exclude(
                pk=self.instance.pk if self.instance else None
            ).exists()

            if room_conflict:
                raise serializers.ValidationError(
                    'Room already has a session during this time.'
                )

        return attrs