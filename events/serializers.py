from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Event, Registration


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_staff']


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user


class EventSerializer(serializers.ModelSerializer):
    registered_count = serializers.IntegerField(read_only=True)
    available_seats = serializers.IntegerField(read_only=True)
    is_full = serializers.BooleanField(read_only=True)
    is_past = serializers.BooleanField(read_only=True)
    organizer_name = serializers.CharField(source='organizer.username', read_only=True)

    class Meta:
        model = Event
        fields = [
            'id',
            'title',
            'description',
            'category',
            'location',
            'date',
            'capacity',
            'organizer',
            'organizer_name',
            'image_url',
            'is_active',
            'registered_count',
            'available_seats',
            'is_full',
            'is_past',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'organizer', 'created_at', 'updated_at']


class RegistrationSerializer(serializers.ModelSerializer):
    event_title = serializers.CharField(source='event.title', read_only=True)
    event_date = serializers.DateTimeField(source='event.date', read_only=True)
    event_location = serializers.CharField(source='event.location', read_only=True)

    class Meta:
        model = Registration
        fields = [
            'id',
            'ticket_code',
            'event',
            'event_title',
            'event_date',
            'event_location',
            'user',
            'full_name',
            'email',
            'phone',
            'notes',
            'status',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'ticket_code', 'user', 'status', 'created_at', 'updated_at']


class RegistrationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Registration
        fields = [
            'event',
            'full_name',
            'email',
            'phone',
            'notes'
        ]

    def validate(self, attrs):
        event = attrs.get('event')
        email = attrs.get('email')

        if not event.is_active:
            raise serializers.ValidationError({"event": "This event is currently inactive and not accepting registrations."})

        if event.is_full:
            raise serializers.ValidationError({"event": "Sorry, this event is already fully booked."})

        # Check existing confirmed registration
        if Registration.objects.filter(event=event, email__iexact=email, status=Registration.STATUS_CONFIRMED).exists():
            raise serializers.ValidationError({"email": "You are already registered for this event with this email address."})

        return attrs
