from relais.models import Club, Federation, Company, School
import json
from django.core.serializers.json import DjangoJSONEncoder


def add_get_club(name):
    if name:
        i, _ = Club.objects.get_or_create(name=name)
    else:
        i = None
    return i

def add_get_fede(name):
    if name:
        i, _ = Federation.objects.get_or_create(name=name)
    else:
        i = None
    return i

def add_get_company(name):
    if name:
        i, _ = Company.objects.get_or_create(name=name)
    else:
        i = None
    return i

def add_get_school(name):
    if name:
        i, _ = School.objects.get_or_create(name=name)
    else:
        i = None
    return i

def get_all_autocomplete():
    a = {}
    a['school'] = json.dumps(list(School.objects.all().values_list('name', flat=True)),
                             cls=DjangoJSONEncoder)
    a['club'] = json.dumps(list(Club.objects.all().values_list('name', flat=True)),
                           cls=DjangoJSONEncoder)
    a['federation'] = json.dumps(list(Federation.objects.all().values_list('name', flat=True)),
                                 cls=DjangoJSONEncoder)
    a['company'] = json.dumps(list(Company.objects.all().values_list('name', flat=True)),
                              cls=DjangoJSONEncoder)
    return a
