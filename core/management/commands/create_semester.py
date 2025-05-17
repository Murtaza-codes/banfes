from django.core.management.base import BaseCommand, CommandError
from core.models import Session, Semester
from django.utils import timezone


class Command(BaseCommand):
    help = 'Creates a new semester and optionally sets it as the current semester'

    def add_arguments(self, parser):
        parser.add_argument('semester_name', type=str, help='The name of the semester (e.g. "First" or "Second")')
        parser.add_argument(
            '--session', 
            type=str, 
            help='The session this semester belongs to (must already exist). If not provided, uses current session.'
        )
        parser.add_argument(
            '--current',
            action='store_true',
            help='Set this semester as the current semester',
        )
        parser.add_argument(
            '--next-begins',
            type=str,
            help='Next semester begins date (YYYY-MM-DD). Defaults to six months from now.',
        )

    def handle(self, *args, **options):
        semester_name = options['semester_name']
        session_name = options['session']
        make_current = options['current']
        next_begins = options['next_begins']

        # Get the session
        if session_name:
            try:
                session = Session.objects.get(session=session_name)
            except Session.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Session "{session_name}" does not exist.'))
                return
        else:
            # Use current session if session not specified
            session = Session.objects.filter(is_current_session=True).first()
            if not session:
                self.stdout.write(self.style.ERROR('No current session found. Please create a session first.'))
                return

        # Check if this semester already exists for this session
        if Semester.objects.filter(semester=semester_name, session=session).exists():
            self.stdout.write(self.style.ERROR(f'Semester "{semester_name}" already exists for session {session}.'))
            return

        # Default next_begins to six months from now if not provided
        if not next_begins:
            next_six_months = timezone.now() + timezone.timedelta(days=180)
            next_begins = next_six_months.date()

        # If making this the current semester, unset any existing current semesters
        if make_current:
            Semester.objects.filter(is_current_semester=True).update(is_current_semester=False)
            self.stdout.write(self.style.SUCCESS('Unset previous current semester.'))

        # Create the new semester
        semester = Semester.objects.create(
            semester=semester_name,
            is_current_semester=make_current,
            session=session,
            next_semester_begins=next_begins
        )

        self.stdout.write(self.style.SUCCESS(
            f'Successfully created semester "{semester_name}" for session "{session}"{" and set it as current" if make_current else ""}.'
        )) 