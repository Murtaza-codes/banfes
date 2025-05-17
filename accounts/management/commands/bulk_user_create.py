import csv
import random, string

from django.core.management.base import BaseCommand, CommandError

from accounts.models import User, Student
from course.models import Program

def __random_password__():
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))

def __random_username__(fname, lname):
    return f'{fname}-{lname}-'+''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(6))


class Command(BaseCommand):
    """
    Bulk creates custom users from a CSV file.
    provide a CSV file with the following columns index, firstname, lastname, is_student, is_lecturer, gender, level, program_id

    Example:
        python manage.py bulk_create_custom_users /path/to/users.csv
    """

    help = "Bulk create users from a CSV file"

    def add_arguments(self, parser):
        parser.add_argument('-p', '--path', type=str, help='Path to the CSV file containing user data.')

    def handle(self, *args, **options):
        csv_file_path = options['path']

        # Get your custom user model (e.g., CustomUser)
        # User = get_user_model()
        report_data = []
        # Read and process the CSV file
        try:
            programs = { program.id: program for program in Program.objects.all() }
            with open(csv_file_path, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                # For performance, we can collect user objects in a list
                # and bulk_create them in one go.
                users_to_create = []
                students_to_create = []
                for row in reader:
                    # Adjust these based on the fields in your CSV
                    fname = row.get('firstname')
                    lname = row.get('lastname')
                    is_student = row.get('is_student', '0') == '1'
                    is_lecturer = row.get('is_lecturer', '0') == '1'
                    gender = row.get('gender')

                    if not (fname and lname and gender):
                        self.stdout.write(self.style.WARNING(
                            f"Skipping row due to missing data: {row}"
                        ))
                        continue

                    if is_lecturer and is_student:
                        self.stdout.write(self.style.WARNING(
                            f"Cannot be both lecturer and student. Skipping row: {row}"
                        ))
                        continue
                    
                    # Prepare a user instance. For example:
                    username = __random_username__(fname, lname)
                    password = __random_password__()

                    user = User(
                        username=username,
                        is_lecturer=is_lecturer,
                        is_student=is_student,
                        gender=gender,
                        first_name=fname,
                        last_name=lname,
                    )
                    user.set_password(password)

                    users_to_create.append(user)

                    report_data.append({
                        "firstname": fname,
                        "lastname": lname,
                        "username": username,
                        "password": password
                    })

                    if not is_student:
                        continue

                    level = row.get('level')
                    program_id = int(row.get('program_id'))
                    program = programs.get(program_id, None)
                    if program is None:
                        self.stdout.write(self.style.WARNING(
                                f"No such program with id {program_id}. Skipping student creation for row: {row}"
                            ))
                        continue
                    student = Student(
                        student=user,
                        level=level,
                        program=program,
                    )
                    students_to_create.append(student)
                    

                # Bulk create all valid users
                if users_to_create:
                    User.objects.bulk_create(users_to_create)
                    self.stdout.write(self.style.SUCCESS(
                        f"Successfully created {len(users_to_create)} user(s)."
                    ))
                    if students_to_create:
                        Student.objects.bulk_create(students_to_create)
                        self.stdout.write(self.style.SUCCESS(
                            f"Successfully created {len(students_to_create)} students(s)."
                        ))
                else:
                    self.stdout.write(self.style.WARNING(
                        "No valid rows found to create users."
                    ))
            
            if report_data:
                with open("report.csv", mode="w", newline="", encoding="utf-8") as output_file:
                    fieldnames = ["firstname", "lastname", "username", "password"]
                    writer = csv.DictWriter(output_file, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(report_data)

                self.stdout.write(self.style.SUCCESS(
                    "report.csv generated successfully with user information."
                ))
            else:
                self.stdout.write(self.style.WARNING(
                    "No report.csv generated because no users were created."
                ))

        
        except FileNotFoundError:
            raise CommandError(f"File {csv_file_path} does not exist.")
        except Exception as e:
            raise CommandError(f"An error occurred while reading the CSV file: {e}")

