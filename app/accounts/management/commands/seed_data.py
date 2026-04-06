from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

User = get_user_model()

SEED_EMAILS = [
    "admin@example.com",
    "alice@example.com",
    "bob@example.com",
    "carol@example.com",
    "dave@example.com",
    "eve@example.com",
    "frank@example.com",
    "grace@example.com",
    "henry@example.com",
    "iris@example.com",
    "jack@example.com",
    "kate@example.com",
    "leo@example.com",
    "mia@example.com",
    "noah@example.com",
]


class Command(BaseCommand):
    help = "Populate the database with realistic seed data for development and testing"

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing seed data and reseed from scratch",
        )

    def handle(self, *args, **options):
        if User.objects.filter(email="admin@example.com").exists():
            if not options["reset"]:
                self.stdout.write("Seed data already present. Use --reset to reseed.")
                return
            self.stdout.write("Resetting seed data...")
            User.objects.filter(email__in=SEED_EMAILS).delete()

        self._create_users()
        self._create_events()
        self.stdout.write(self.style.SUCCESS("Seed data created successfully."))
        self.stdout.write("")
        self.stdout.write("  Logins (password: testpass123)")
        self.stdout.write("  Admin:     admin@example.com")
        self.stdout.write("  Organizer: alice@example.com  |  bob@example.com")
        self.stdout.write("  Attendees: carol@example.com … noah@example.com")

    # ------------------------------------------------------------------ #
    # Users                                                                #
    # ------------------------------------------------------------------ #

    def _create_users(self):
        self.stdout.write("Creating users...")

        self.admin = User.objects.create_superuser(
            email="admin@example.com",
            password="testpass123",
            name="Admin User",
            is_organizer=True,
        )
        self.alice = User.objects.create_user(
            email="alice@example.com",
            password="testpass123",
            name="Alice Organizer",
            is_organizer=True,
        )
        self.bob = User.objects.create_user(
            email="bob@example.com",
            password="testpass123",
            name="Bob Organizer",
            is_organizer=True,
        )

        attendee_data = [
            ("carol@example.com", "Carol Attendee"),
            ("dave@example.com", "Dave Attendee"),
            ("eve@example.com", "Eve Attendee"),
            ("frank@example.com", "Frank Attendee"),
            ("grace@example.com", "Grace Attendee"),
            ("henry@example.com", "Henry Attendee"),
            ("iris@example.com", "Iris Attendee"),
            ("jack@example.com", "Jack Attendee"),
            ("kate@example.com", "Kate Attendee"),
            ("leo@example.com", "Leo Attendee"),
            ("mia@example.com", "Mia Attendee"),
            ("noah@example.com", "Noah Attendee"),
        ]
        self.attendees = {}
        for email, name in attendee_data:
            self.attendees[email.split("@")[0]] = User.objects.create_user(
                email=email, password="testpass123", name=name
            )

        self.stdout.write(f"  Created {15} users.")

    # ------------------------------------------------------------------ #
    # Events, tracks, speakers, sessions, registrations                   #
    # ------------------------------------------------------------------ #

    def _create_events(self):
        from app.events.models import Event
        from app.registrations.models import Registration
        from app.sessions.models import Session, Speaker
        from app.tracks.models import Track

        now = timezone.now()
        # All events placed ~30 days in the future so date filters work
        base = now.replace(hour=0, minute=0, second=0, microsecond=0) + timezone.timedelta(days=30)

        # ---- DjangoCon Europe 2026 (published, max=10, starts FULL) ---- #
        self.stdout.write("Creating DjangoCon Europe 2026...")
        djangocon = Event.objects.create(
            title="DjangoCon Europe 2026",
            description=(
                "The premier European conference for Django developers. "
                "Three days of talks, workshops, and sprints covering the latest "
                "in Django, REST APIs, deployment, and the Python ecosystem."
            ),
            start_date=base,
            end_date=base + timezone.timedelta(days=3),
            venue_name="Convention Centre Dublin",
            venue_address="Spencer Dock, North Wall Quay, Dublin 1, Ireland",
            max_attendees=10,
            organizer=self.alice,
            status=Event.Status.PUBLISHED,
        )

        dc_web = Track.objects.create(event=djangocon, name="Web Development", color="#6366f1")
        dc_ops = Track.objects.create(event=djangocon, name="DevOps", color="#f59e0b")

        sarah = Speaker.objects.create(
            name="Dr. Sarah Chen",
            bio="Django core contributor and author of 'Django at Scale'. Previously Staff Engineer at Google.",
            company="Google",
            user=self.alice,
        )
        marcus = Speaker.objects.create(
            name="Marcus Webb",
            bio="Open source advocate and platform engineer. Maintainer of several popular Django packages.",
            company="Red Hat",
        )

        Session.objects.create(
            title="Keynote: Django 5 — What's New and What's Next",
            description="An overview of the headline features in Django 5 and a sneak peek at the roadmap.",
            track=dc_web,
            speaker=sarah,
            start_time=base.replace(hour=9),
            end_time=base.replace(hour=10),
            room="Main Hall",
            session_type=Session.SessionType.KEYNOTE,
        )
        Session.objects.create(
            title="Building REST APIs with DRF and drf-spectacular",
            description="Practical guide to building versioned, documented APIs using Django REST Framework.",
            track=dc_web,
            speaker=marcus,
            start_time=base.replace(hour=10),
            end_time=base.replace(hour=11),
            room="Main Hall",
            session_type=Session.SessionType.TALK,
        )
        Session.objects.create(
            title="Deploying Django with Docker and GitHub Actions",
            description="End-to-end walkthrough: multi-stage Dockerfile, docker-compose, and a production-ready CI/CD pipeline.",
            track=dc_ops,
            speaker=marcus,
            start_time=base.replace(hour=9),
            end_time=base.replace(hour=10, minute=30),
            room="Workshop Room A",
            session_type=Session.SessionType.WORKSHOP,
        )
        Session.objects.create(
            title="CI/CD Best Practices for Django Projects",
            description="Testing strategies, deployment gates, and rollback patterns for Django in production.",
            track=dc_ops,
            speaker=sarah,
            start_time=base.replace(hour=10, minute=30),
            end_time=base.replace(hour=11, minute=30),
            room="Workshop Room A",
            session_type=Session.SessionType.TALK,
        )

        # Fill DjangoCon to capacity: 10 confirmed registrations
        djangocon_attendees = [
            self.attendees["carol"], self.attendees["dave"], self.attendees["eve"],
            self.attendees["frank"], self.attendees["grace"], self.attendees["henry"],
            self.attendees["iris"], self.attendees["jack"], self.attendees["kate"],
            self.attendees["noah"],
        ]
        for attendee in djangocon_attendees:
            Registration.objects.create(
                attendee=attendee, event=djangocon, status=Registration.Status.CONFIRMED
            )
        self.stdout.write(f"  DjangoCon: {len(djangocon_attendees)}/10 confirmed (FULL — next registration waitlists)")

        # ---- PyCon APAC 2026 (published, max=10, partially filled) ---- #
        self.stdout.write("Creating PyCon APAC 2026...")
        pycon_base = base + timezone.timedelta(days=60)
        pycon = Event.objects.create(
            title="PyCon APAC 2026",
            description=(
                "Python community conference for the Asia-Pacific region. "
                "Sessions covering core Python, data science, ML, and web development."
            ),
            start_date=pycon_base,
            end_date=pycon_base + timezone.timedelta(days=2),
            venue_name="Suntec Singapore Convention & Exhibition Centre",
            venue_address="1 Raffles Boulevard, Suntec City, Singapore 039593",
            max_attendees=10,
            organizer=self.alice,
            status=Event.Status.PUBLISHED,
        )

        pc_core = Track.objects.create(event=pycon, name="Python Core", color="#10b981")
        pc_data = Track.objects.create(event=pycon, name="Data Science", color="#ef4444")

        yuki = Speaker.objects.create(
            name="Yuki Tanaka",
            bio="CPython contributor and Python Software Foundation fellow. Specialises in async and performance.",
            company="Microsoft",
        )
        priya = Speaker.objects.create(
            name="Priya Sharma",
            bio="ML engineer and open source contributor. Builds developer tools at scale.",
            company="HashiCorp",
        )

        Session.objects.create(
            title="Python 3.13 — What's New",
            description="A deep dive into the new features, performance improvements, and deprecations in Python 3.13.",
            track=pc_core,
            speaker=yuki,
            start_time=pycon_base.replace(hour=9),
            end_time=pycon_base.replace(hour=10),
            room="Auditorium",
            session_type=Session.SessionType.KEYNOTE,
        )
        Session.objects.create(
            title="Async Python Deep Dive",
            description="Understanding asyncio, structured concurrency, and real-world async patterns in Python.",
            track=pc_core,
            speaker=yuki,
            start_time=pycon_base.replace(hour=10),
            end_time=pycon_base.replace(hour=11),
            room="Auditorium",
            session_type=Session.SessionType.TALK,
        )
        Session.objects.create(
            title="From Pandas to Polars: A Migration Guide",
            description="When and how to migrate data pipelines from Pandas to Polars for better performance.",
            track=pc_data,
            speaker=priya,
            start_time=pycon_base.replace(hour=9),
            end_time=pycon_base.replace(hour=10, minute=30),
            room="Room B",
            session_type=Session.SessionType.WORKSHOP,
        )

        # PyCon: partially filled (3 confirmed, 1 cancelled)
        Registration.objects.create(attendee=self.attendees["carol"], event=pycon, status=Registration.Status.CONFIRMED)
        Registration.objects.create(attendee=self.attendees["dave"], event=pycon, status=Registration.Status.CONFIRMED)
        Registration.objects.create(attendee=self.attendees["eve"], event=pycon, status=Registration.Status.CONFIRMED)
        Registration.objects.create(attendee=self.attendees["henry"], event=pycon, status=Registration.Status.CANCELLED)
        self.stdout.write("  PyCon: 3/10 confirmed, 1 cancelled")

        # ---- Cloud Native Summit (bob's event, published, partially filled) ---- #
        self.stdout.write("Creating Cloud Native Summit...")
        cn_base = base + timezone.timedelta(days=45)
        cloud = Event.objects.create(
            title="Cloud Native Summit 2026",
            description=(
                "A conference for platform engineers and DevOps practitioners. "
                "Covering Kubernetes, observability, GitOps, and cloud-native architecture."
            ),
            start_date=cn_base,
            end_date=cn_base + timezone.timedelta(days=2),
            venue_name="ExCeL London",
            venue_address="Royal Victoria Dock, 1 Western Gateway, London E16 1XL, UK",
            max_attendees=10,
            organizer=self.bob,
            status=Event.Status.PUBLISHED,
        )

        cn_k8s = Track.objects.create(event=cloud, name="Kubernetes", color="#3b82f6")
        cn_obs = Track.objects.create(event=cloud, name="Observability", color="#8b5cf6")

        Session.objects.create(
            title="Introduction to Kubernetes for Developers",
            description="A hands-on workshop covering pods, deployments, services, and ingress from scratch.",
            track=cn_k8s,
            speaker=priya,
            start_time=cn_base.replace(hour=9),
            end_time=cn_base.replace(hour=10, minute=30),
            room="Workshop Hall",
            session_type=Session.SessionType.WORKSHOP,
            capacity=20,
        )
        Session.objects.create(
            title="Kubernetes Networking Deep Dive",
            description="CNI plugins, network policies, service mesh options, and debugging connectivity issues.",
            track=cn_k8s,
            speaker=marcus,
            start_time=cn_base.replace(hour=10, minute=30),
            end_time=cn_base.replace(hour=12),
            room="Workshop Hall",
            session_type=Session.SessionType.PANEL,
        )
        Session.objects.create(
            title="OpenTelemetry in Production",
            description="Instrumenting Python services with OpenTelemetry, shipping traces and metrics to Grafana.",
            track=cn_obs,
            speaker=sarah,
            start_time=cn_base.replace(hour=9),
            end_time=cn_base.replace(hour=10),
            room="Room C",
            session_type=Session.SessionType.TALK,
        )

        Registration.objects.create(attendee=self.attendees["frank"], event=cloud, status=Registration.Status.CONFIRMED)
        Registration.objects.create(attendee=self.attendees["grace"], event=cloud, status=Registration.Status.CONFIRMED)
        Registration.objects.create(attendee=self.attendees["iris"], event=cloud, status=Registration.Status.CANCELLED)
        self.stdout.write("  Cloud Native: 2/10 confirmed, 1 cancelled")

        # ---- Django Workshop (draft, invisible to public) ---- #
        self.stdout.write("Creating Django Workshop (draft)...")
        Event.objects.create(
            title="Django Internals Workshop",
            description=(
                "A deep-dive workshop into Django internals: ORM query compilation, "
                "middleware pipeline, template engine, and the request/response cycle."
            ),
            start_date=base + timezone.timedelta(days=90),
            end_date=base + timezone.timedelta(days=91),
            venue_name="Online",
            venue_address="Zoom",
            max_attendees=10,
            organizer=self.alice,
            status=Event.Status.DRAFT,
        )
        self.stdout.write("  Draft event created (not visible to public)")
