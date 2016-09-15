import http
import json

from django.http.response import (
    HttpResponseNotAllowed,
    HttpResponseBadRequest,
    HttpResponse,
)
from django.utils.dateparse import parse_time
from django.views.decorators.csrf import csrf_exempt

from relais.models import Runner
from relais.util.decorator import logged_in_or_basicauth


#------------------------------------------------------------------------------
@csrf_exempt
@logged_in_or_basicauth()
def set_time(request):
    """
    Set a time to a Runner.

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
        runner = Runner.objects.filter(num=num).get()
    except Runner.DoesNotExist:
        return HttpResponseBadRequest('runner with number %s is unknown' % num)

    runner.time = time
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
@logged_in_or_basicauth()
def get_runner(request):
    """
    Set a time to a Runner.

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
        runner = Runner.objects.filter(num=num).get()
    except Runner.DoesNotExist:
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
