from _functools import reduce
from collections import namedtuple, OrderedDict
from datetime import timedelta
import operator
import random

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render

from relais import constants, helpers
from relais.helpers import cat2hash, get_relais_categories, get_years_ffa
from relais.helpers.development import create_fake_runner
from relais.models import (
    Company,
    Payment,
    Price,
    People,
    Runner,
)


RESULTS = namedtuple('Results', ['name', 'results'])
#------------------------------------------------------------------------------
@login_required
def index(request):
    """
    Home page
    """
    stats = {}
    stats['nb_runner'] = len(People.objects.all())
    stats['nb_indiv'] = len(helpers.get_all_indiv())
    stats['nb_team'] = len(helpers.get_all_indiv())
    return render(request, 'management/home.html', stats)

#------------------------------------------------------------------------------
@login_required
def timing(request):
    """
    Timing page
    """
    return render(request, 'management/timing.html')

#------------------------------------------------------------------------------
@login_required
def timing_auto(request):
    """
    Timing page
    """
    return render(request, 'management/timing_auto.html')

#------------------------------------------------------------------------------
@login_required
def start_race(request):
    """
    Start race page
    """
    return render(request, 'management/start_race.html')

#------------------------------------------------------------------------------
@login_required
def listing(request):
    """
    Listing individuals or teams
    """
    to_template = {
        'cat': get_relais_categories(),
        'individual': helpers.get_all_indiv(),  # all individuals registered
        'team': helpers.get_all_team(),  # all teams registered
    }

    return render(request, 'management/listing.html', to_template)

#------------------------------------------------------------------------------
@login_required
def results(request):
    """
    Show all results
    """
    indiv = helpers.get_all_indiv()
    team = helpers.get_all_team()
    to_template = {
        'cat': get_relais_categories(),
        'individual': [RESULTS(name="Tous les résultats individuels",
                                      results=indiv.order_by('runner_1__time'))],
        'team': [RESULTS(name="Tous les résultats équipes",
                     results=team.order_by('runner_3__time'))],
    }

    to_template['order_by_time'] = True
    return render(request, 'management/results.html', to_template)

#------------------------------------------------------------------------------
@login_required
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
        limit_1 = None
        limit_3 = None
    else:
        limit_1 = 1
        limit_3 = 3

    individual = helpers.get_all_indiv() 

    if order_by_time:
        order = 'runner_1__time'
        individual = individual.filter(runner_1__time__gt=timedelta(0, 0, 0))
    else:
        order = 'runner_1__num'

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
    for i in individual:
        c = cat2hash(i.runner_1.runner_category())
        ffa[c][i.runner_1.gender].append(i.pk)

    # when iterate on a dict, data are not ordered
    # let's use a OrderedDict
    # generate list of "recompense"
    r_cat = OrderedDict()
    r_cat[constants.V1] = {'name': '%s (%s)' % (constants.V1, get_years_ffa(constants.V1)), 'ffa': True}
    r_cat[constants.V2] = {'name': '%s (%s)' % (constants.V2, get_years_ffa(constants.V2)), 'ffa': True}
    r_cat[constants.V3] = {'name': '%s (%s)' % (constants.V3, get_years_ffa(constants.V3)), 'ffa': True}
    r_cat[constants.V4] = {'name': '%s (%s)' % (constants.V4, get_years_ffa(constants.V4)), 'ffa': True}
    r_cat[constants.ESPOIR] = {'name': '%s (%s)' % (constants.ESPOIR, get_years_ffa(constants.ESPOIR)), 'ffa': True}
    r_cat[constants.SENOIR] = {'name': '%s (%s)' % (constants.SENOIR, get_years_ffa(constants.SENOIR)), 'ffa': True}
    r_cat[constants.JUNIOR] = {'name': '%s (%s)' % (constants.JUNIOR, get_years_ffa(constants.JUNIOR)), 'ffa': True}
    r_cat[constants.CADET] = {'name': '%s (%s)' % (constants.CADET, get_years_ffa(constants.CADET)), 'ffa': True}
    r_cat[constants.STUDENT_ENSIL_ENSCI] = {'name': 'Etudiant ENSIL-ENSCI', 'ffa': False}
    r_cat[constants.STUDENT] = {'name': 'Etudiant', 'ffa': False}
    r_cat[constants.CHALLENGE] = {'name': 'Challenge entreprise', 'ffa': False}
    r_cat[constants.OLDER] = {'name': 'Ancien de l\'ENSIL-ENSCI', 'ffa': False}

    people = OrderedDict()
    people[constants.MALE] = 'Homme'
    people[constants.FEMALE] = 'Femme'

    # End of configuration
    # Begin of get results
    query = individual.filter(runner_1__gender=constants.MALE)
    query = query.order_by(order)
    r.append(RESULTS(name="Scratch Homme",
                     results=query[0:limit_3]))

    query = individual.filter(runner_1__gender=constants.FEMALE)
    query = query.order_by(order)
    r.append(RESULTS(name="Scratch Femme",
                            results=query[0:limit_3]))

    for key_gender, name_gender in people.items():
        # exclude 3 first one runners Male / Female
        if display_all:
            exclude = []
        else:
            exclude = individual.filter(runner_1__gender=key_gender).order_by(order)[0:limit_3]

        for key, data in r_cat.items():
            name = "{category} - {gender}".format(category=data['name'],
                                                  gender=name_gender)
            if data['ffa']:
                # FFA specificities
                hash_cat = cat2hash(key)
                runner_in_category = ffa[hash_cat][key_gender]

                query = individual.filter(id__in=runner_in_category)
                query = query.exclude(pk__in=exclude)
                query = query.order_by(order)
            else:
                # Relais specificities
                # No exclusion for Relais specificities (cumul)
                query = individual.filter(category=key, runner_1__gender=key_gender)
                query = query.order_by(order)

            # get results
            results = query[0:limit_1]
            r.append(RESULTS(name=name, results=results))

    r.append(RESULTS(name="La tenue originale (non géré automatiquement)",
                            results=[]))

    query = individual.order_by('-runner_1__time')
    r.append(RESULTS(name="Le dernier",
                            results=query[0:limit_1]))

    to_template['individual'] = r
    to_template['order_by_time'] = order_by_time

    return render(request, 'management/results.html', to_template)

#------------------------------------------------------------------------------
@login_required
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
        limit_1 = None
        limit_3 = None
    else:
        limit_1 = 1
        limit_3 = 3

    team = helpers.get_all_team()

    if order_by_time:
        order = 'runner_3__time'
        team = team.filter(runner_1__time__gt=timedelta(0, 0, 0),
                           runner_2__time__gt=timedelta(0, 0, 0),
                           runner_3__time__gt=timedelta(0, 0, 0))
    else:
        order = 'runner_3__num'

    # So... It is quite hard for Team to get results with a good algorithm like
    # as Individual
    # Let's do it manually
    r = []

    # Male
    query = team.filter(runner_1__gender=constants.MALE,
                        runner_2__gender=constants.MALE,
                        runner_3__gender=constants.MALE)
    query = query.order_by(order)

    r.append(RESULTS(name="Homme",
                            results=query[0:limit_3]))

    # Female
    query = team.filter(runner_1__gender=constants.FEMALE,
                        runner_2__gender=constants.FEMALE,
                        runner_3__gender=constants.FEMALE)
    query = query.order_by(order)

    r.append(RESULTS(name="Femme",
                            results=query[0:limit_3]))

    # Mixte 1
    mixte1 = [(constants.FEMALE, constants.MALE, constants.MALE),
               (constants.MALE, constants.FEMALE, constants.MALE),
               (constants.MALE, constants.MALE, constants.FEMALE)]

    q_mixte1 = [Q(runner_1__gender=x[0],
                  runner_2__gender=x[1],
                  runner_3__gender=x[2])
                for x in mixte1]

    query = team.filter(reduce(operator.or_, q_mixte1))  # convert list into x1 OR x2 ...
    query = query.order_by(order)

    r.append(RESULTS(name="Mixte 1",
                            results=query[0:limit_1]))
    # Mixte 2
    mixte2 = [(constants.MALE, constants.FEMALE, constants.FEMALE),
               (constants.FEMALE, constants.MALE, constants.FEMALE),
               (constants.FEMALE, constants.FEMALE, constants.MALE)]

    q_mixte2 = [Q(runner_1__gender=x[0],
                  runner_2__gender=x[1],
                  runner_3__gender=x[2])
                for x in mixte2]

    query = team.filter(reduce(operator.or_, q_mixte2))  # convert list into x1 OR x2 ...
    query = query.order_by(order)

    r.append(RESULTS(name="Mixte 2",
                     results=query[0:limit_1]))

    # College
    # need to parse school name
    q_college = [Q(runner_1__school__name__icontains=x,
                   runner_2__school__name__icontains=x,
                   runner_3__school__name__icontains=x)
                 for x in ['college', 'collège']]

    query = team.filter(category=constants.STUDENT)
    query = query.filter(reduce(operator.or_, q_college))
    query = query.order_by(order)
    r.append(RESULTS(name="Collégiens",
                        results=query[0:limit_1]))

    # 5) Lycée
    # need to parse school names
    q_lycee = [Q(runner_1__school__name__icontains=x,
                 runner_2__school__name__icontains=x,
                 runner_3__school__name__icontains=x)
               for x in ['lycee', 'lycée']]

    query = team.filter(category=constants.STUDENT)
    query = query.filter(reduce(operator.or_, q_lycee))
    query = query.order_by(order)

    r.append(RESULTS(name="Lycéens",
                        results=query[0:limit_1]))

    # 6) Etudiant M
    student = {}
    query = team.filter(Q(category=constants.STUDENT) |
                        Q(category=constants.STUDENT_ENSIL_ENSCI))
    query = query.filter(runner_1__gender=constants.MALE,
                         runner_2__gender=constants.MALE,
                         runner_3__gender=constants.MALE)
    query = query.exclude(reduce(operator.or_, q_college))  # exclude college
    query = query.exclude(reduce(operator.or_, q_lycee))  # exclude lycee
    query = query.order_by(order)

    student['male'] = query[0:limit_1]
    r.append(RESULTS(name="Etudiants - Homme",
                            results=student['male']))

    # Etudiant F
    query = team.filter(Q(category=constants.STUDENT) |
                        Q(category=constants.STUDENT_ENSIL_ENSCI))
    query = query.filter(runner_1__gender=constants.FEMALE,
                         runner_2__gender=constants.FEMALE,
                         runner_3__gender=constants.FEMALE)
    query = query.exclude(reduce(operator.or_, q_college))  # exclude college
    query = query.exclude(reduce(operator.or_, q_lycee))  # exclude lycee
    query = query.order_by(order)

    student['female'] = query[0:limit_1]

    r.append(RESULTS(name="Etudiants - Femme",
                            results=student['female']))

    # Etudiant mixte
    q_mixte = [Q(runner_1__gender=x,
                 runner_2__gender=x,
                 runner_3__gender=x)
               for x in [constants.MALE, constants.FEMALE]]

    query = team.filter(Q(category=constants.STUDENT) |
                        Q(category=constants.STUDENT_ENSIL_ENSCI))
    query = query.exclude(reduce(operator.or_, q_mixte))  # exlude M/M/M or F/F/F
    query = query.exclude(reduce(operator.or_, q_college))  # exclude college
    query = query.exclude(reduce(operator.or_, q_lycee))  # exclude lycee
    query = query.order_by(order)

    student['mix'] = query[0:limit_1]

    r.append(RESULTS(name="Etudiants - Mixte",
                        results=student['mix']))

    # XXX: find another way to do this
    if display_all:
        # Do not exclude ENSIL-ENSCI people when display all
        student['male'] = []
        student['female'] = []
        student['mix'] = []

    # ENSIL-ENSCI M
    query = team.filter(category=constants.STUDENT_ENSIL_ENSCI)
    query = query.filter(runner_1__gender=constants.MALE,
                         runner_2__gender=constants.MALE,
                         runner_3__gender=constants.MALE)
    query = query.exclude(pk__in=student['male'])
    query = query.order_by(order)

    r.append(RESULTS(name="ENSIL-ENSCI - Homme",
                    results=query[0:limit_1]))

    # ENSIL-ENSCI F
    query = team.filter(category=constants.STUDENT_ENSIL_ENSCI)
    query = query.filter(runner_1__gender=constants.FEMALE,
                         runner_2__gender=constants.FEMALE,
                         runner_3__gender=constants.FEMALE)
    query = query.exclude(pk__in=student['female'])
    query = query.order_by(order)

    r.append(RESULTS(name="ENSIL-ENSCI - Femme",
                    results=query[0:limit_1]))

    # ENSIL-ENSCI mixte
    query = team.filter(category=constants.STUDENT_ENSIL_ENSCI)
    query = query.exclude(reduce(operator.or_, q_mixte))  # exlude M/M/M or F/F/F
    query = query.exclude(pk__in=student['mix'])
    query = query.order_by(order)

    r.append(RESULTS(name="ENSIL-ENSCI - Mixte",
                    results=query[0:limit_1]))

    # Challenge M
    query = team.filter(category=constants.CHALLENGE)
    query = query.filter(runner_1__gender=constants.MALE,
                         runner_2__gender=constants.MALE,
                         runner_3__gender=constants.MALE)
    query = query.order_by(order)

    r.append(RESULTS(name="Challenge Entreprise - Homme",
                        results=query[0:limit_1]))

    # Challenge F
    query = team.filter(category=constants.CHALLENGE)
    query = query.filter(runner_1__gender=constants.FEMALE,
                         runner_2__gender=constants.FEMALE,
                         runner_3__gender=constants.FEMALE)
    query = query.order_by(order)

    r.append(RESULTS(name="Challenge Entreprise - Femme",
                        results=query[0:limit_1]))

    # Challenge mixte
    query = team.filter(category=constants.CHALLENGE)
    query = query.exclude(reduce(operator.or_, q_mixte))  # exlude M/M/M or F/F/F
    query = query.order_by(order)

    r.append(RESULTS(name="Challenge Entreprise - Mixte",
                        results=query[0:limit_1]))

    # Anciens ENSIL-ENSCI
    query = team.filter(category=constants.OLDER)
    query = query.order_by(order)

    r.append(RESULTS(name="Anciens ENSIL-ENSCI",
                            results=query[0:limit_1]))

    to_template['team'] = r
    to_template['order_by_time'] = order_by_time

    return render(request, 'management/results.html', to_template)

#------------------------------------------------------------------------------
@login_required
def create_fake_users(request):
    # for this test, I will generate fictive individual
    r = []
    cat = {}
    cat[0] = constants.ADULT
    cat[1] = constants.CHALLENGE
    cat[2] = constants.STUDENT
    cat[3] = constants.STUDENT_ENSIL_ENSCI
    cat[4] = constants.OLDER

    People.objects.all().delete()
    Runner.objects.all().delete()
    Payment.objects.all().delete()
    word_file = "/usr/share/dict/words"
    words = open(word_file).read().splitlines()

    for i in range(0, 250):
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
        r = [None] * 3
        name = None
        if indiv:
            r[0] = create_fake_runner(category, True, school_name=school)
        else:
            for i in range(0, 3):
                r[i] = create_fake_runner(category, False, school_name=school, num=i)
            name = words[random.randint(0, len(words))]
        run = Runner(name=name, runner_1=r[1],
                 runner_2=r[2], runner_3=r[3], category=category, payment=pay,
                 company=company)
        run.save()

    return render(request)
