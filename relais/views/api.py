from datetime import datetime, timezone, timedelta
import http
import json

from django.http.response import (
    HttpResponseNotAllowed,
    HttpResponseBadRequest,
    HttpResponse,
)
from django.utils.dateparse import parse_time
from django.views.decorators.csrf import csrf_exempt

from relais.models import People, Setting


#------------------------------------------------------------------------------
@csrf_exempt
def set_time(request):
    """
    Set a time to a People.

    Accept only POST request with parameters:
    :arg int num:
        The bib number of the runner
    :arg str/time time:
        A time format (like hh:mm:ss)

    :returns:
        A JSON data with some runner informations.
    """
    # sanity checks
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    for param in ('num', 'time'):
        if param not in request.POST:
            return HttpResponseBadRequest('missing parameter %r' % param)
    try:
        num = int(request.POST['num'])
    except ValueError:
        return HttpResponseBadRequest('num must be an integer')

    try:
        time = parse_time(request.POST['time'])
        if not time:
            raise ValueError
    except ValueError:
        return HttpResponseBadRequest('"time" must be HH:MM[:ss[.uuuuuu]]')

    try:
        runner = People.objects.filter(num=num).get()
    except People.DoesNotExist:
        return HttpResponseBadRequest('runner with number %s is unknown' % num)

    runner.time = timedelta(days=0, minutes=time.minute, seconds=time.second)
    runner.save()

    response = {
        'first_name': runner.first_name,
        'last_name': runner.last_name,
        'num': runner.num,
        'time': str(runner.time),
    }

    return HttpResponse(json.dumps(response),
                        status=http.HTTPStatus.CREATED,
                        content_type='application/json')

#------------------------------------------------------------------------------
@csrf_exempt
def set_dynamic_time(request):
    """
    Set a time to a People.

    Accept only POST request with parameters:
    :arg int num:
        The bib number of the runner

    :returns:
        A JSON data with some runner informations.
    """
    # sanity checks
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

        if 'num' not in request.POST:
            return HttpResponseBadRequest('missing parameter %r' % 'num')
    try:
        num = int(request.POST['num'])
    except ValueError:
        return HttpResponseBadRequest('num must be an integer')

    try:
        runner = People.objects.filter(num=num).get()
    except People.DoesNotExist:
        return HttpResponseBadRequest('runner with number %s is unknown' % num)

    s = Setting.objects.get()
    delta = datetime.now(timezone.utc) - s.start
    runner.time = delta
    runner.save()
    runner = People.objects.filter(num=num).get()

    response = {
        'first_name': runner.first_name,
        'last_name': runner.last_name,
        'num': runner.num,
        'time': str(runner.time),
    }

    return HttpResponse(json.dumps(response),
                        status=http.HTTPStatus.CREATED,
                        content_type='application/json')

@csrf_exempt
def set_top_time_dynamic(request):
    """
    :returns:
        A JSON data with some runner informations.
    """
    # sanity checks
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    s = Setting.objects.get()
    s.start = datetime.now(timezone.utc)
    s.save()
    s = Setting.objects.get()

    response = {
        'timestamp': str(s.start),
    }

    return HttpResponse(json.dumps(response),
                        status=http.HTTPStatus.CREATED,
                        content_type='application/json')

#------------------------------------------------------------------------------
@csrf_exempt
def get_runner(request):
    """
    Set a time to a People.

    Accept only POST request with parameters:
    :arg int num:
        The bib number of the runner
    :arg str/time time:
        A time format (like hh:mm:ss)

    :returns:
        A JSON data with some runner informations.
    """
    # sanity checks
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    if 'num' not in request.POST:
        return HttpResponseBadRequest('missing parameter %r' % 'num')

    try:
        num = int(request.POST['num'])
    except ValueError:
        return HttpResponseBadRequest('num must be an integer')

    try:
        runner = People.objects.filter(num=num).get()
    except People.DoesNotExist:
        return HttpResponseBadRequest('runner with number %s is unknown' % num)

    response = {
        'first_name': runner.first_name,
        'last_name': runner.last_name,
        'num': runner.num,
        'time': str(runner.time),
    }

    return HttpResponse(json.dumps(response),
                        status=http.HTTPStatus.CREATED,
                        content_type='application/json')
