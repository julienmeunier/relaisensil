import hashlib
import json

from django.core.serializers.json import DjangoJSONEncoder

from relais.models import Club, Federation, Company, School, CATEGORY_CHOICES


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

def cat2hash(category):
    """
    Hash a category string in order to be usable in dict for example.

    :arg str category:
        A category string.

    :returns:
        A hash of this category string
    """
    return hashlib.md5(category.encode('utf-8')).hexdigest()

def get_relais_categories():
    """
    Convert a list of tuple ((a,b),(c,d)) to a dict
    """
    cat = {}
    for key, name in CATEGORY_CHOICES:
        cat[key] = name
    return cat
