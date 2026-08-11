"""
To get API input and make it to User obj and make the pass safe.
"""


from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import User, ConsultantProfile


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'name']
        extra_kwargs = {
            'password': {
                'write_only': True,
                'min_length': 8,
            },
        }

    def create(self, validated_data):
        return get_user_model().objects.create_user(
            **validated_data,
        )


class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ['email', 'name']
        read_only_fields = ['email']


class ConsultantSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        source='user.name',
        read_only=True,
    )

    class Meta:
        model = ConsultantProfile
        fields = [
            'id',
            'name',
            'preferred_start_time',
        ]
        read_only_fields = [
            'id',
            'name',
        ]


class ConsultantCreateSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True,
        min_length=5,
    )
    name = serializers.CharField()
    preferred_start_time = serializers.TimeField()

    def create(self, validated_data):
        preferred_start_time = validated_data.pop(
            'preferred_start_time',
        )

        user = User.objects.create_user(
            **validated_data,
        )

        return ConsultantProfile.objects.create(
            user=user,
            preferred_start_time=preferred_start_time,
        )

    def to_representation(self, instance):
        return {
            'id': instance.id,
            'email': instance.user.email,
            'name': instance.user.name,
            'preferred_start_time': instance.preferred_start_time,
        }