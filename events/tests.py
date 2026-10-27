from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Event, Registration


class EventRegistrationAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testorganizer',
            password='password123',
            email='organizer@example.com'
        )
        self.attendee_user = User.objects.create_user(
            username='testattendee',
            password='password123',
            email='attendee@example.com'
        )
        self.event = Event.objects.create(
            title='Backend Architecture Summit',
            description='A summit on scalable backend architecture.',
            category='TECH',
            location='Online',
            date=timezone.now() + timedelta(days=10),
            capacity=2,
            organizer=self.user,
            is_active=True
        )

    def test_event_list_api(self):
        """Test retrieving the list of active events."""
        url = reverse('api_events_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Backend Architecture Summit')
        self.assertEqual(response.data[0]['available_seats'], 2)

    def test_event_detail_api(self):
        """Test retrieving single event details."""
        url = reverse('api_event_detail', kwargs={'pk': self.event.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.event.id)
        self.assertEqual(response.data['capacity'], 2)
        self.assertEqual(response.data['registered_count'], 0)

    def test_successful_registration(self):
        """Test attendee can successfully submit a registration."""
        url = reverse('api_event_register', kwargs={'event_id': self.event.id})
        data = {
            'full_name': 'Kamran Mammadov',
            'email': 'kamran@example.com',
            'phone': '+994 50 111 22 33',
            'notes': 'Excited to attend!'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('registration', response.data)
        self.assertEqual(response.data['registration']['email'], 'kamran@example.com')
        self.assertTrue(response.data['registration']['ticket_code'].startswith('EVT-'))

        # Verify available seats decreased
        self.event.refresh_from_db()
        self.assertEqual(self.event.registered_count, 1)
        self.assertEqual(self.event.available_seats, 1)

    def test_duplicate_registration_prevention(self):
        """Test that same email cannot register twice for same event."""
        url = reverse('api_event_register', kwargs={'event_id': self.event.id})
        data = {
            'full_name': 'Kamran Mammadov',
            'email': 'kamran@example.com'
        }
        # First registration
        r1 = self.client.post(url, data, format='json')
        self.assertEqual(r1.status_code, status.HTTP_201_CREATED)

        # Second registration with same email
        r2 = self.client.post(url, data, format='json')
        self.assertEqual(r2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', r2.data)

    def test_event_capacity_limit(self):
        """Test registration rejected when event capacity is reached."""
        url = reverse('api_event_register', kwargs={'event_id': self.event.id})
        # Event capacity is 2
        self.client.post(url, {'full_name': 'User 1', 'email': 'user1@test.com'}, format='json')
        self.client.post(url, {'full_name': 'User 2', 'email': 'user2@test.com'}, format='json')

        self.event.refresh_from_db()
        self.assertTrue(self.event.is_full)

        # 3rd registration attempt should fail
        r3 = self.client.post(url, {'full_name': 'User 3', 'email': 'user3@test.com'}, format='json')
        self.assertEqual(r3.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cancel_registration_and_free_seat(self):
        """Test cancelling a registration marks it cancelled and frees capacity."""
        reg = Registration.objects.create(
            event=self.event,
            full_name='Cancel Test',
            email='cancel@test.com',
            status=Registration.STATUS_CONFIRMED
        )
        self.event.refresh_from_db()
        self.assertEqual(self.event.registered_count, 1)

        # Cancel endpoint
        cancel_url = reverse('api_registration_cancel', kwargs={'pk': reg.id})
        response = self.client.post(cancel_url, {'email': 'cancel@test.com'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        reg.refresh_from_db()
        self.assertEqual(reg.status, Registration.STATUS_CANCELLED)

        self.event.refresh_from_db()
        self.assertEqual(self.event.registered_count, 0)
        self.assertEqual(self.event.available_seats, 2)

    def test_my_registrations_api(self):
        """Test retrieving registrations by email."""
        Registration.objects.create(
            event=self.event,
            full_name='Search Test',
            email='lookup@example.com',
            status=Registration.STATUS_CONFIRMED
        )
        url = f"{reverse('api_my_registrations')}?email=lookup@example.com"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['email'], 'lookup@example.com')


class WebViewsTestCase(TestCase):
    def setUp(self):
        self.event = Event.objects.create(
            title='Web Demo Event',
            description='Testing templates and routing',
            category='TECH',
            location='Online',
            date=timezone.now() + timedelta(days=3),
            capacity=20
        )

    def test_home_page(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Web Demo Event')

    def test_event_detail_page(self):
        response = self.client.get(reverse('event_detail', kwargs={'pk': self.event.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Web Demo Event')
        self.assertContains(response, 'Register Now')

    def test_api_docs_page(self):
        response = self.client.get(reverse('api_docs'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'REST API Documentation')
