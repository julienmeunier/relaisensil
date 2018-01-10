import hashlib
import json

from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.functions.base import Now

from relais.models import Club, Federation, Company, School, Runner, CATEGORY_CHOICES
from relais import constants


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

def get_years_ffa(category):
    """
    Category are given by FFA
    """
    today_year = datetime.today().year
    if category == constants.POUSSIN:
        r = '< %s' % (today_year - 9)
    elif category == constants.PUPILLE:
        r  = '%s - %s' % (today_year - 11, today_year - 10)
    elif category == constants.BENJAMIN:
        r  = '%s - %s' % (today_year - 13, today_year - 12)
    elif category == constants.MINIME:
        r  = '%s - %s' % (today_year - 15, today_year - 14)
    elif category == constants.CADET:
        r  = '%s - %s' % (today_year - 17, today_year - 16)
    elif category == constants.JUNIOR:
        r  = '%s - %s' % (today_year - 19, today_year - 18)
    elif category == constants.ESPOIR:
        r  = '%s - %s' % (today_year - 22, today_year - 20)
    elif category == constants.SENOIR:
        r  = '%s - %s' % (today_year - 39, today_year - 23)
    elif category == constants.V1:
        r  = '%s - %s' % (today_year - 49, today_year - 40)
    elif category == constants.V2:
        r  = '%s - %s' % (today_year - 59, today_year - 50)
    elif category == constants.V3:
        r  = '%s - %s' % (today_year - 69, today_year - 60)
    elif category == constants.V4:
        r  = '> %s' % (today_year - 70)
    else:
        r = 'Unknown category'

    return r

def get_all_indiv():
    return Runner.objects.filter(runner_1__isnull=False,
                                 runner_2__isnull=True,
                                 runner_3__isnull=True)

def get_all_team():
    return Runner.objects.filter(runner_1__isnull=False,
                                 runner_2__isnull=False,
                                 runner_3__isnull=False)
