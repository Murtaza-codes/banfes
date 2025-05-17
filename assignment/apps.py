from django.apps import AppConfig

class AssignmentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'assignment'

    def ready(self):
        # Import the translation module when the app is ready
        from . import translation
