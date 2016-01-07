from functools import wraps

from django.shortcuts import render
from django.utils import timezone
from django.utils.decorators import available_attrs

from relais.models import Setting


def registration_opened():
    """
    Decorator to make a view only if registrations are opened.  Usage::

        @registration_opened()
        def my_view(request):
    """
    def decorator(func):
        @wraps(func, assigned=available_attrs(func))
        def inner(request, *args, **kwargs):
            setting = Setting.objects.get()
            begin = setting.open_online
            end = setting.closure_online
            event = setting.event
            now = timezone.now()
            if begin <= now and now <= end:
                return func(request, *args, **kwargs)
            else:
                data = {}
                data['event'] = event
                data['begin'] = begin
                if begin >= now:
                    data['too_late'] = True
                else:
                    data['too_late'] = False
                return render(request, 'registration/closed.html', data)
        return inner
    return decorator
    