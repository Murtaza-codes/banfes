# TODO

- **School calendar**
  - School calendar should be implemented displayed on the home page along with news and events
  - Managed by admin/superadmin
- **News and events**
  - News and events should be associated with the calendar
- **Add and Drop**:
  - Department head
  - The add and drop page should only include courses offered by the department head.
  - Add and drop date should be restricted by the school calendar.
- **Payment integration**:
  - Integrating PayPal and Stripe for students to pay their fees.
- **Integrate the dashboard with dynamic/live data**:
  - Overall attendance
  - School demographics
    - Lecturer qualification
    - Students' level
  - Students average grade per course:
    This helps to keep track of students' performance
  - Overall Course Resources
    - Total number of videos, courses, documentation
  - Event calendar:
    - A calendar that shows upcoming events
  - Enrollments per course
    - How many students enroll in each course
  - Website traffic over a specific user type (Admin, Student, Lecturer, etc.)
- **Apply data exporting for all tables**:
  - This can be done using jQuery libraries like `DataTables`
- **Using a template to PDF converter to generate reports**:
  - This can be done using the popular package `xhtml2pdf`

# Making Migrations:

docker-compose exec web python manage.py makemigrations

docker-compose exec web python manage.py migrate

# To preview changes in SCSS:

docker-compose exec web python manage.py collectstatic

# Login Credentials for student account:
7E72Mfz4Eb
ugr-2024-4
B4KbAXzTr7
# Login Credentials for teacher account:

lec-2024-1

# Login Credentials for admin account:

python manage.py createsuperuser

# Login Credentials for superadmin account:

AgateAdmin
agate123

# Connect to Postgres

psql -h localhost -p 5432 -U agate_admin -d agatedb


http://127.0.0.1:8000/en/quiz/dari-101/assignments/

