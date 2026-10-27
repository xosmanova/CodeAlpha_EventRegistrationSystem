from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from events.models import Event, Registration


class Command(BaseCommand):
    help = 'Seeds database with sample users, events, and registrations for CodeAlpha testing and demo'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('[*] Starting database seeding...'))

        # 1. Create Superuser (Admin)
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@codealpha.tech',
                'first_name': 'CodeAlpha',
                'last_name': 'Administrator',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('[+] Created superuser: admin / admin123'))
        else:
            self.stdout.write(self.style.SUCCESS('[i] Superuser admin already exists.'))

        # 2. Create Regular Test User
        demo_user, created = User.objects.get_or_create(
            username='john_doe',
            defaults={
                'email': 'john.doe@example.com',
                'first_name': 'John',
                'last_name': 'Doe',
            }
        )
        if created:
            demo_user.set_password('password123')
            demo_user.save()
            self.stdout.write(self.style.SUCCESS('[+] Created demo user: john_doe / password123'))

        now = timezone.now()

        # 3. Create Sample Events
        events_data = [
            {
                'title': 'CodeAlpha Global Tech Summit 2026',
                'description': 'Join software engineers, backend architects, and tech leaders from around the world for keynote talks, panel discussions, and technical deep-dives on the future of scalable cloud software, microservices, and AI-driven automation.',
                'category': 'TECH',
                'location': 'Baku Expo & Convention Center / Live Hybrid Stream',
                'date': now + timedelta(days=14, hours=3),
                'capacity': 100,
                'image_url': 'https://images.unsplash.com/photo-1540575467063-178a50c2df87?auto=format&fit=crop&w=1200&q=80',
            },
            {
                'title': 'Full-Stack Web Development Bootcamp: Django & Modern Frontend',
                'description': 'An intensive, hands-on workshop covering backend API development with Django REST Framework, database schema design, authentication, and responsive frontend architectures.',
                'category': 'WORKSHOP',
                'location': 'Innovation Hub, Hall B, Baku',
                'date': now + timedelta(days=7, hours=2),
                'capacity': 30,
                'image_url': 'https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?auto=format&fit=crop&w=1200&q=80',
            },
            {
                'title': 'Applied AI & Large Language Models Symposium',
                'description': 'Explore cutting-edge developments in autonomous AI agents, multi-modal LLMs, and real-time inference pipelines. Featuring live demonstrations and research showcases.',
                'category': 'SEMINAR',
                'location': 'ADA University Auditorium / Virtual Zoom',
                'date': now + timedelta(days=21, hours=5),
                'capacity': 75,
                'image_url': 'https://images.unsplash.com/photo-1485827404703-89b55fcc595e?auto=format&fit=crop&w=1200&q=80',
            },
            {
                'title': 'CodeAlpha 48-Hour Hackathon 2026',
                'description': 'Build groundbreaking projects in 48 hours! Form teams, brainstorm, architect backend solutions, and pitch to leading tech venture capitalists and senior engineers.',
                'category': 'HACKATHON',
                'location': 'Tech Park Campus, Incubator Space',
                'date': now + timedelta(days=28, hours=10),
                'capacity': 40,
                'image_url': 'https://images.unsplash.com/photo-1504384308090-c894fdcc538d?auto=format&fit=crop&w=1200&q=80',
            },
            {
                'title': 'Tech Career Networking & Mentorship Mixer',
                'description': 'Connect with recruiters, senior mentors, and fellow interns. Resume review booths, mock technical interviews, and 1-on-1 engineering networking sessions.',
                'category': 'NETWORKING',
                'location': 'Grand Terrace Lounge, Baku',
                'date': now + timedelta(days=35, hours=6),
                'capacity': 50,
                'image_url': 'https://images.unsplash.com/photo-1511578314322-379afb476865?auto=format&fit=crop&w=1200&q=80',
            },
            {
                'title': 'Microservices & Database Optimization Masterclass (Exclusive)',
                'description': 'Exclusive intimate masterclass focusing on high-throughput database index optimization, SQL caching, and transactional integrity under heavy concurrent loads.',
                'category': 'WORKSHOP',
                'location': 'Online Private Webinar Room',
                'date': now + timedelta(days=5, hours=4),
                'capacity': 2,
                'image_url': 'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=1200&q=80',
            }
        ]

        created_events = []
        for e_data in events_data:
            event, _ = Event.objects.get_or_create(
                title=e_data['title'],
                defaults={
                    'description': e_data['description'],
                    'category': e_data['category'],
                    'location': e_data['location'],
                    'date': e_data['date'],
                    'capacity': e_data['capacity'],
                    'organizer': admin_user,
                    'image_url': e_data['image_url'],
                    'is_active': True
                }
            )
            created_events.append(event)

        self.stdout.write(self.style.SUCCESS(f'[+] Seeded {len(created_events)} events.'))

        # 4. Seed Registrations
        sample_attendees = [
            ("John Doe", "john.doe@example.com", "+994 50 111 22 33", demo_user),
            ("Leyla Mammadova", "leyla@example.com", "+994 55 222 33 44", None),
            ("Rashad Aliyev", "rashad@example.com", "+994 70 333 44 55", None),
            ("Aysel Huseynova", "aysel@example.com", "+994 51 444 55 66", None),
        ]

        # Register attendees to first event
        first_event = created_events[0]
        for name, email, phone, u in sample_attendees:
            if not Registration.objects.filter(event=first_event, email=email).exists():
                Registration.objects.create(
                    event=first_event,
                    user=u,
                    full_name=name,
                    email=email,
                    phone=phone,
                    status=Registration.STATUS_CONFIRMED,
                    notes="Looking forward to the sessions!"
                )

        # Fill the exclusive masterclass to test full capacity logic
        exclusive_event = created_events[-1]
        for name, email in [("Masterclass Attendee 1", "att1@test.com"), ("Masterclass Attendee 2", "att2@test.com")]:
            if not Registration.objects.filter(event=exclusive_event, email=email).exists():
                Registration.objects.create(
                    event=exclusive_event,
                    full_name=name,
                    email=email,
                    phone="+994 50 999 88 77",
                    status=Registration.STATUS_CONFIRMED
                )

        self.stdout.write(self.style.SUCCESS('[+] Database seeding completed successfully!'))
        self.stdout.write(self.style.SUCCESS('[>] Admin credentials: admin / admin123'))
        self.stdout.write(self.style.SUCCESS('[>] Demo user credentials: john_doe / password123'))
