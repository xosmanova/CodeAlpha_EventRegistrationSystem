import uuid
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone


class Event(models.Model):
    CATEGORY_CHOICES = [
        ('TECH', 'Technology & AI'),
        ('WORKSHOP', 'Workshop & Hands-on'),
        ('SEMINAR', 'Seminar & Conference'),
        ('HACKATHON', 'Hackathon'),
        ('NETWORKING', 'Networking & Career'),
        ('OTHER', 'General Event'),
    ]

    title = models.CharField(max_length=200, help_text="Title of the event")
    description = models.TextField(help_text="Detailed description of the event")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='TECH')
    location = models.CharField(max_length=255, help_text="Physical venue address or 'Online / Zoom'")
    date = models.DateTimeField(help_text="Date and time when the event takes place")
    capacity = models.PositiveIntegerField(default=50, help_text="Maximum number of attendees")
    organizer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='organized_events',
        null=True,
        blank=True,
        help_text="Event organizer or creator"
    )
    image_url = models.URLField(
        blank=True,
        default='',
        help_text="Banner or poster image URL"
    )
    is_active = models.BooleanField(default=True, help_text="Active events accept registrations")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date']
        verbose_name = 'Event'
        verbose_name_plural = 'Events'

    def __str__(self):
        return f"{self.title} ({self.date.strftime('%Y-%m-%d %H:%M') if self.date else 'No Date'})"

    @property
    def registered_count(self):
        return self.registrations.filter(status='CONFIRMED').count()

    @property
    def available_seats(self):
        return max(0, self.capacity - self.registered_count)

    @property
    def is_full(self):
        return self.registered_count >= self.capacity

    @property
    def is_past(self):
        return self.date < timezone.now()


class Registration(models.Model):
    STATUS_CONFIRMED = 'CONFIRMED'
    STATUS_CANCELLED = 'CANCELLED'

    STATUS_CHOICES = [
        (STATUS_CONFIRMED, 'Confirmed'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='registrations'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='registrations',
        help_text="Registered user account (optional for guest registration)"
    )
    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True, help_text="Dietary needs, special requests, or notes")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_CONFIRMED
    )
    ticket_code = models.CharField(
        max_length=16,
        unique=True,
        editable=False,
        help_text="Unique ticket reference code"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Registration'
        verbose_name_plural = 'Registrations'

    def __str__(self):
        return f"{self.full_name} -> {self.event.title} [{self.ticket_code}] ({self.status})"

    def clean(self):
        super().clean()
        # If new or updating to confirmed, check capacity and duplicates
        if self.status == self.STATUS_CONFIRMED:
            # Check duplicate active registration for same email & event
            existing = Registration.objects.filter(
                event=self.event,
                email__iexact=self.email,
                status=self.STATUS_CONFIRMED
            )
            if self.pk:
                existing = existing.exclude(pk=self.pk)
            if existing.exists():
                raise ValidationError("A confirmed registration with this email already exists for this event.")

            # Check capacity only when newly registering or changing status to CONFIRMED
            if not self.pk or (self.pk and Registration.objects.filter(pk=self.pk, status=self.STATUS_CANCELLED).exists()):
                if self.event.is_full:
                    raise ValidationError("This event is fully booked. No seats are available.")

    def save(self, *args, **kwargs):
        if not self.ticket_code:
            self.ticket_code = f"EVT-{uuid.uuid4().hex[:8].upper()}"
        self.full_clean()
        super().save(*args, **kwargs)

    def cancel(self):
        """Cancel this registration and free up a seat."""
        self.status = self.STATUS_CANCELLED
        self.save(update_fields=['status', 'updated_at'])
