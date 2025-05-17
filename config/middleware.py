# middleware.py
from django.utils import timezone
import pytz

class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Try to get timezone from browser
            tzname = request.COOKIES.get('timezone')
            if tzname:
                try:
                    timezone.activate(pytz.timezone(tzname))
                    if request.user.timezone != tzname:
                        request.user.timezone = tzname
                        request.user.save()
                except:
                    pass
        return self.get_response(request)