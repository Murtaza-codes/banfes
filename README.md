## Current features

- Dashboard: School demographics and analytics. Restricted to only admins
- News And Events: All users can access this page
- Admin manages students(Add, Update, Delete)
- Admin manages lecturers(Add, Update, Delete)
- Students can Add and Drop courses
- Lecturers submit students' scores: _Attendance, Mid exam, Final exam, assignment_
- The system calculates students' _Total, average, point, and grades automatically_
- Grade comment for each student with a **pass**, **fail**, or **pass with a warning**
- Assessment result page for students
- Grade result page for students
- Session/year and semester management
- Assessments and grades will be grouped by semester
- Upload video and documentation for each course
- PDF generator for students' registration slip and grade result
- Page access restriction
- Storing of quiz results under each user
- Question order randomization
- Previous quiz scores can be viewed on the category page
- Correct answers can be shown after each question or all at once at the end
- Logged-in users can return to an incomplete quiz to finish it and non-logged-in users can complete a quiz if their session persists
- The quiz can be limited to one attempt per user
- Questions can be given a category
- Success rate for each category can be monitored on a progress page
- Explanation for each question result can be given
- Pass marks can be set
- Multiple choice question type
- True/False question type............_Coming soon_
- Essay question type................._Coming soon_
- Custom message displayed for those that pass or fail a quiz
- Custom permission (view_sittings) added, allowing users with that permission to view quiz results from users
- A marking page which lists completed quizzes, can be filtered by quiz or user, and is used to mark essay questions

# Requirements:

> The following program(s) are required to run the project

- [Python3.8+](https://www.python.org/downloads/)
- [PostgreSQL](https://www.postgresql.org/download/) (if running with PostgreSQL database)

# Installation

## Running with Docker

- Clone the repo with

- Create and run the docker containers

```bash
    docker-compose up -d
```

- Create `.env` file inside the root directory

- Copy and paste everything in the `.env.example` file into the `.env` file. Don't forget to customize the variable values

```bash
   docker compose run web python manage.py migrate
```

```bash
   docker compose run web python manage.py createsuperuser
```

```bash
    docker compose up
```

## Running without Docker

You can run the application with SQLite (default) or PostgreSQL:

### Option 1: Using SQLite (Easiest)

This is configured by default in the settings.py file. Just follow these steps:

1. Create a `.env` file in the root directory with the following content:
```
SECRET_KEY="o!ld8nrt4vc*h1zoey*wj48x*q0#ss12h=+zh)kk^6b3aygg=!"
DEBUG=True
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=youremail@example.com
EMAIL_HOST_PASSWORD=yourpassword
EMAIL_FROM_ADDRESS=youremail@example.com
STRIPE_SECRET_KEY=your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run migrations:
```bash
python manage.py migrate
```

4. Create a superuser:
```bash
python manage.py createsuperuser
```

5. Start the development server:
```bash
python manage.py runserver
```

### Option 2: Using PostgreSQL

1. Install PostgreSQL and create a database

2. Create a `.env` file in the root directory with the following content (adjust values as needed):
```
POSTGRES_DB=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=fum12435968
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
SECRET_KEY="o!ld8nrt4vc*h1zoey*wj48x*q0#ss12h=+zh)kk^6b3aygg=!"
DEBUG=True
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=youremail@example.com
EMAIL_HOST_PASSWORD=yourpassword
EMAIL_FROM_ADDRESS=youremail@example.com
STRIPE_SECRET_KEY=your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key
```

3. In config/settings.py, update the database configuration to use PostgreSQL:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB', 'postgres'),
        'USER': os.getenv('POSTGRES_USER', 'postgres'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'fum12435968'),
        'HOST': os.getenv('POSTGRES_HOST', 'localhost'),
        'PORT': os.getenv('POSTGRES_PORT', '5432'),
    },
}
```

4. Follow steps 2-5 from Option 1 above.

Last but not least, go to this address http://127.0.0.1:8000
