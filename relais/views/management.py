#-*-coding: utf-8 -*-
from collections import namedtuple
import operator
import random

from django.db.models import Q
from django.shortcuts import render

from relais import constants
from relais.helpers import cat2hash, get_relais_categories
from relais.helpers.development import create_fake_runner
from relais.models import (
    Company,
    Individual,
    Payment,
    Price,
    Runner,
    TSHIRT_CHOICES,
    Team,
)
from relais.util.decorator import logged_in_or_basicauth
from relais.util.ordereddict import OrderedDict


RESULTS = namedtuple('Results', ['name', 'results'])
#------------------------------------------------------------------------------
@logged_in_or_basicauth()
def index(request):
    """
    Home page
    """
    stats = {}
    stats['nb_runner'] = len(Runner.objects.all())
    stats['nb_indiv'] = len(Individual.objects.all())
    stats['nb_team'] = len(Team.objects.all())
    return render(request, 'management/home.html', stats)

#------------------------------------------------------------------------------
@logged_in_or_basicauth()
def listing(request):
    """
    Listing individuals or teams
    """
    to_template = {
        'cat': get_relais_categories(),
        'individual': Individual.objects.all(),  # all individuals registered
        'team': Team.objects.all(),  # all teams registered
    }

    return render(request, 'management/listing.html', to_template)

#------------------------------------------------------------------------------
@logged_in_or_basicauth()
def results(request):
    """
    Show all results
    """
    to_template = {
        'cat': get_relais_categories(),
        'individual': [RESULTS(name="Tous les résultats individuels",
                                      results=Individual.objects.order_by('runner__time'))],
        'team': [RESULTS(name="Tous les résultats équipes",
                     results=Team.objects.order_by('runner_3__time'))],
    }

    return render(request, 'management/results.html', to_template)

#------------------------------------------------------------------------------
@logged_in_or_basicauth()
def results_individual(request, display_all=False, order_by_time=True):
    """
    Display only individual results

    :arg bool display_all:
        Show final results or only people who are recompenzed ?
    :arg bool order_by_time:
        List results by time or by number.
        Be careful, if False, final classement are wrong !
    """
    cat = get_relais_categories()

    to_template = {
        'cat': cat,
    }

    # 
    if display_all:
        count_1 = None
        count_3 = None
    else:
        count_1 = 1
        count_3 = 3

    if order_by_time:
        order = 'runner__time'
    else:
        order = 'runner__num'

    r = []


    # generate dict with FFA categories -> individual
    ffa = {}
    for c in constants.CATEGORIES:
        h = cat2hash(c)
        ffa[h] = {}
        ffa[h]['name'] = c
        ffa[h][constants.MALE] = []
        ffa[h][constants.FEMALE] = []

    # compute FFA people
    # eg: ffa[category][male] = list of people
    for i in Individual.objects.all():
        c = cat2hash(i.runner.runner_category())
        ffa[c][i.runner.gender].append(i.pk)

    # when iterate on a dict, data are not ordered
    # let's use a OrderedDict
    # generate list of "recompense"
    r_cat = OrderedDict()
    r_cat[constants.V1] = {'name': constants.V1, 'ffa': True}
    r_cat[constants.V2] = {'name': constants.V2, 'ffa': True}
    r_cat[constants.V3] = {'name': constants.V3, 'ffa': True}
    r_cat[constants.V4] = {'name': constants.V4, 'ffa': True}
    r_cat[constants.ESPOIR] = {'name': constants.ESPOIR, 'ffa': True}
    r_cat[constants.SENOIR] = {'name': constants.SENOIR, 'ffa': True}
    r_cat[constants.JUNIOR] = {'name': constants.JUNIOR, 'ffa': True}
    r_cat[constants.CADET] = {'name': constants.CADET, 'ffa': True}
    r_cat[constants.CHALLENGE] = {'name': 'Challenge entreprise', 'ffa': False}
    r_cat[constants.OLDER_ENSIL] = {'name': 'Ancien de l\'ENSIL', 'ffa': False}

    people = OrderedDict()
    people[constants.MALE] = 'Homme'
    people[constants.FEMALE] = 'Femme'

    # End of configuration
    # Begin of get results
    query = Individual.objects.filter(runner__gender=constants.MALE)
    query = query.order_by(order)
    r.append(RESULTS(name="Scratch Homme",
                     results=query[0:count_3]))

    query = Individual.objects.filter(runner__gender=constants.FEMALE)
    query = query.order_by(order)
    r.append(RESULTS(name="Scratch Femme",
                            results=query[0:count_3]))

    for key_gender, name_gender in people.iteritems():
        # exclude 3 first one runners Male / Female
        if display_all:
            exclude = []
        else:
            exclude = Individual.objects.filter(runner__gender=key_gender).order_by(order)[0:count_3]

        for key, data in r_cat.iteritems():
            name = "{category} - {gender}".format(category=data['name'],
                                                  gender=name_gender)
            if data['ffa']:
                # FFA specificities
                hash_cat = cat2hash(key)
                runner_in_category = ffa[hash_cat][key_gender]

                query = Individual.objects.filter(id__in=runner_in_category)
                query = query.exclude(pk__in=exclude)
                query = query.order_by(order)
            else:
                # Relais specificities
                # No exclusion for Relais specificities (cumul)
                query = Individual.objects.filter(category=key, runner__gender=key_gender)
                query = query.order_by(order)

            # get results
            results = query[0:count_1]
            r.append(RESULTS(name=name, results=results))

    r.append(RESULTS(name="La tenue originale (non géré automatiquement)",
                            results=[]))

    query = Individual.objects.order_by('-runner__time')
    r.append(RESULTS(name="Le dernier",
                            results=query[0:count_1]))

    to_template['individual'] = r

    return render(request, 'management/results.html', to_template)

#------------------------------------------------------------------------------
@logged_in_or_basicauth()
def results_team(request, display_all=False, order_by_time=True):
    """
    Display only team results

    :arg bool display_all:
        Show final results or only people who are recompenzed ?
    :arg bool order_by_time:
        List results by time or by number.
        Be careful, if False, final classement are wrong !
    """
    cat = get_relais_categories()

    to_template = {
        'cat': cat,
    }

    if display_all:
        count_1 = None
        count_3 = None
    else:
        count_1 = 1
        count_3 = 3

    if order_by_time:
        order = 'runner_3__time'
    else:
        order = 'runner_3__num'

    # So... It is quite hard for Team to get results with a good algorithm like
    # as Individual
    # Let's do it manually
    r = []

    # Male
    query = Team.objects.filter(runner_1__gender=constants.MALE,
                        runner_2__gender=constants.MALE,
                        runner_3__gender=constants.MALE)
    query = query.order_by(order)

    r.append(RESULTS(name="Homme",
                            results=query[0:count_3]))

    # Female
    query = Team.objects.filter(runner_1__gender=constants.FEMALE,
                        runner_2__gender=constants.FEMALE,
                        runner_3__gender=constants.FEMALE)
    query = query.order_by(order)

    r.append(RESULTS(name="Femme",
                            results=query[0:count_3]))

    # Mixte 1
    mixte1 = [(constants.FEMALE, constants.MALE, constants.MALE),
               (constants.MALE, constants.FEMALE, constants.MALE),
               (constants.MALE, constants.MALE, constants.FEMALE)]

    q_mixte1 = [Q(runner_1__gender=x[0],
                  runner_2__gender=x[1],
                  runner_3__gender=x[2])
                for x in mixte1]

    query = Team.objects.filter(reduce(operator.or_, q_mixte1))  # convert list into x1 OR x2 ...
    query = query.order_by(order)

    r.append(RESULTS(name="Mixte 1",
                            results=query[0:count_1]))
    # Mixte 2
    mixte2 = [(constants.MALE, constants.FEMALE, constants.FEMALE),
               (constants.FEMALE, constants.MALE, constants.FEMALE),
               (constants.FEMALE, constants.FEMALE, constants.MALE)]

    q_mixte2 = [Q(runner_1__gender=x[0],
                  runner_2__gender=x[1],
                  runner_3__gender=x[2])
                for x in mixte2]

    query = Team.objects.filter(reduce(operator.or_, q_mixte2))  # convert list into x1 OR x2 ...
    query = query.order_by(order)

    r.append(RESULTS(name="Mixte 2",
                     results=query[0:count_1]))

    # College
    # need to parse school name
    q_college = [Q(runner_1__school__name__icontains=x,
                   runner_2__school__name__icontains=x,
                   runner_3__school__name__icontains=x)
                 for x in ['college', 'collège']]

    query = Team.objects.filter(category=constants.STUDENT)
    query = query.filter(reduce(operator.or_, q_college))
    query = query.order_by(order)
    r.append(RESULTS(name="Collégiens",
                        results=query[0:count_1]))

    # 5) Lycée
    # need to parse school names
    q_lycee = [Q(runner_1__school__name__icontains=x,
                 runner_2__school__name__icontains=x,
                 runner_3__school__name__icontains=x)
               for x in ['lycee', 'lycée']]

    query = Team.objects.filter(category=constants.STUDENT)
    query = query.filter(reduce(operator.or_, q_lycee))
    query = query.order_by(order)

    r.append(RESULTS(name="Lycéens",
                        results=query[0:count_1]))

    # 6) Etudiant M
    student = {}
    query = Team.objects.filter(Q(category=constants.STUDENT) |
                        Q(category=constants.STUDENT_ENSIL))
    query = query.filter(runner_1__gender=constants.MALE,
                         runner_2__gender=constants.MALE,
                         runner_3__gender=constants.MALE)
    query = query.exclude(reduce(operator.or_, q_college))  # exclude college
    query = query.exclude(reduce(operator.or_, q_lycee))  # exclude lycee
    query = query.order_by(order)

    student['male'] = query[0:count_1]
    r.append(RESULTS(name="Etudiants - Homme",
                            results=student['male']))

    # Etudiant F
    query = Team.objects.filter(Q(category=constants.STUDENT) |
                        Q(category=constants.STUDENT_ENSIL))
    query = query.filter(runner_1__gender=constants.FEMALE,
                         runner_2__gender=constants.FEMALE,
                         runner_3__gender=constants.FEMALE)
    query = query.exclude(reduce(operator.or_, q_college))  # exclude college
    query = query.exclude(reduce(operator.or_, q_lycee))  # exclude lycee
    query = query.order_by(order)

    student['female'] = query[0:count_1]

    r.append(RESULTS(name="Etudiants - Femme",
                            results=student['female']))

    # Etudiant mixte
    q_mixte = [Q(runner_1__gender=x,
                 runner_2__gender=x,
                 runner_3__gender=x)
               for x in [constants.MALE, constants.FEMALE]]

    query = Team.objects.filter(Q(category=constants.STUDENT) |
                        Q(category=constants.STUDENT_ENSIL))
    query = query.exclude(reduce(operator.or_, q_mixte))  # exlude M/M/M or F/F/F
    query = query.exclude(reduce(operator.or_, q_college))  # exclude college
    query = query.exclude(reduce(operator.or_, q_lycee))  # exclude lycee
    query = query.order_by(order)

    student['mix'] = query[0:count_1]

    r.append(RESULTS(name="Etudiants - Mixte",
                        results=student['mix']))

    # XXX: find another way to do this
    if display_all:
        # Do not exclude ENSIL people when display all
        student['male'] = []
        student['female'] = []
        student['mix'] = []

    # ENSIL M
    query = Team.objects.filter(category=constants.STUDENT_ENSIL)
    query = query.filter(runner_1__gender=constants.MALE,
                         runner_2__gender=constants.MALE,
                         runner_3__gender=constants.MALE)
    query = query.exclude(pk__in=student['male'])
    query = query.order_by(order)

    r.append(RESULTS(name="ENSIL - Homme",
                    results=query[0:count_1]))

    # ENSIL F
    query = Team.objects.filter(category=constants.STUDENT_ENSIL)
    query = query.filter(runner_1__gender=constants.FEMALE,
                         runner_2__gender=constants.FEMALE,
                         runner_3__gender=constants.FEMALE)
    query = query.exclude(pk__in=student['female'])
    query = query.order_by(order)

    r.append(RESULTS(name="ENSIL - Femme",
                    results=query[0:count_1]))

    # ENSIL mixte
    query = Team.objects.filter(category=constants.STUDENT_ENSIL)
    query = query.exclude(reduce(operator.or_, q_mixte))  # exlude M/M/M or F/F/F
    query = query.exclude(pk__in=student['mix'])
    query = query.order_by(order)

    r.append(RESULTS(name="ENSIL - Mixte",
                    results=query[0:count_1]))

    # Challenge M
    query = Team.objects.filter(category=constants.CHALLENGE)
    query = query.filter(runner_1__gender=constants.MALE,
                         runner_2__gender=constants.MALE,
                         runner_3__gender=constants.MALE)
    query = query.order_by(order)

    r.append(RESULTS(name="Challenge Entreprise - Homme",
                        results=query[0:count_1]))

    # Challenge F
    query = Team.objects.filter(category=constants.CHALLENGE)
    query = query.filter(runner_1__gender=constants.FEMALE,
                         runner_2__gender=constants.FEMALE,
                         runner_3__gender=constants.FEMALE)
    query = query.order_by(order)

    r.append(RESULTS(name="Challenge Entreprise - Femme",
                        results=query[0:count_1]))

    # Challenge mixte
    query = Team.objects.filter(category=constants.CHALLENGE)
    query = query.exclude(reduce(operator.or_, q_mixte))  # exlude M/M/M or F/F/F
    query = query.order_by(order)

    r.append(RESULTS(name="Challenge Entreprise - Mixte",
                        results=query[0:count_1]))

    # Anciens ENSILiens
    query = Team.objects.filter(category=constants.OLDER_ENSIL)
    query = query.order_by(order)

    r.append(RESULTS(name="Anciens ENSIL",
                            results=query[0:count_1]))

    to_template['team'] = r

    return render(request, 'management/results.html', to_template)

#------------------------------------------------------------------------------
@logged_in_or_basicauth()
def create_fake_users(request):
    # for this test, I will generate fictive individual
    r = []
    cat = {}
    cat[0] = constants.ADULT
    cat[1] = constants.CHALLENGE
    cat[2] = constants.STUDENT
    cat[3] = constants.STUDENT_ENSIL
    cat[4] = constants.OLDER_ENSIL

    Runner.objects.all().delete()
    Individual.objects.all().delete()
    Team.objects.all().delete()
    Payment.objects.all().delete()
    word_file = "/usr/share/dict/words"
    words = open(word_file).read().splitlines()

    for i in xrange(0, 250):
        category = cat[random.randint(0, 4)]
        school = None
        company = None
        if category == constants.STUDENT:
            type_of_school = random.randint(0, 3)
            if type_of_school == 0:
                school = 'Collège %s' % words[random.randint(0, len(words))]
            elif type_of_school == 1:
                school = 'Lycee %s' % words[random.randint(0, len(words))]
            else:
                school = 'Ecole %s' % words[random.randint(0, len(words))]
        if category == constants.CHALLENGE:
            name_company = 'Entreprise %s' % words[random.randint(0, len(words))]
            company = Company.objects.get_or_create(name=name_company)[0]

        indiv = bool(random.getrandbits(1))
        # dont care about category
        p = Price.objects.filter(when=constants.PRICE_ONLINE,
                                 config=constants.INDIVIDUAL,
                                 who=category).get()
        pay = Payment.objects.create(price=p,
                                     method=constants.CASH,
                                     state=True)
        if indiv:
            r = create_fake_runner(category, True, school_name=school)
            i = Individual(runner=r, category=category, payment=pay, company=company)
            i.save()
        else:
            r = {}
            for i in xrange(1, 4):
                r[i] = create_fake_runner(category, False, school_name=school, num=i)
            t = Team(name=words[random.randint(0, len(words))], runner_1=r[1],
                     runner_2=r[2], runner_3=r[3], category=category, payment=pay,
                     company=company)
            t.save()

    return render(request)
