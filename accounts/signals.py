from django.contrib.auth.hashers import make_password

from .utils import (
    generate_student_credentials,
    generate_lecturer_credentials,
    send_new_account_email,
)

def post_save_account_receiver(instance=None, created=False, *args, **kwargs):
    """
    Send email notification
    """
    if created:
        if instance.is_student or instance.is_lecturer:
            password = make_password(instance.password)
            instance.set_password(password)
            instance.save()
            # Send email with the generated credentials
            # send_new_account_email(instance, password)

        # if instance.is_lecturer:
            # password = make_password(instance.password)
            # instance.set_password(password)
            # instance.save()
            # Send email with the generated credentials
            # send_new_account_email(instance, password)
