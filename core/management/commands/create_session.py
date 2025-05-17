from django.core.management.base import BaseCommand, CommandError
from core.models import Session
from django.utils import timezone


class Command(BaseCommand):
    help = 'Creates a new academic session and optionally sets it as the current session'

    def add_arguments(self, parser):
        parser.add_argument('session_name', type=str, help='The name of the session (e.g. "2024-2025")')
        parser.add_argument(
            '--current',
            action='store_true',
            help='Set this session as the current session',
        )
        parser.add_argument(
            '--next-begins',
            type=str,
            help='Next session begins date (YYYY-MM-DD). Defaults to one year from now.',
        )

    def handle(self, *args, **options):
        session_name = options['session_name']
        make_current = options['current']
        next_begins = options['next_begins']

        # Check if a session with this name already exists
        if Session.objects.filter(session=session_name).exists():
            self.stdout.write(self.style.ERROR(f'Session "{session_name}" already exists.'))
            return

        # Default next_begins to one year from now if not provided
        if not next_begins:
            next_year = timezone.now() + timezone.timedelta(days=365)
            next_begins = next_year.date()

        # If making this the current session, unset any existing current sessions
        if make_current:
            Session.objects.filter(is_current_session=True).update(is_current_session=False)
            self.stdout.write(self.style.SUCCESS('Unset previous current session.'))

        # Create the new session
        session = Session.objects.create(
            session=session_name,
            is_current_session=make_current,
            next_session_begins=next_begins
        )

        self.stdout.write(self.style.SUCCESS(
            f'Successfully created session "{session_name}"{" and set it as current" if make_current else ""}.'
        )) 