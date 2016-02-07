#-*-coding: utf-8 -*-
from collections import namedtuple, OrderedDict
import random

from django.db.models import Q
from django.shortcuts import render

from relais import constants
from relais.helpers import cat2hash, limit_query, get_relais_categories
from relais.models import (
    Individual,
    Payment,
    Price,
    Runner,
    TSHIRT_CHOICES,
    Team
, Company)
from relais.util.decorator import logged_in_or_basicauth
from relais.helpers.development import create_fake_runner
import operator


RESULTS = namedtuple('Results', ['name', 'results'])
#------------------------------------------------------------------------------
@logged_in_or_basicauth()
def index(request):
    """
    Default index page
    """

    return render(request, 'management/home.html')

#------------------------------------------------------------------------------
@logged_in_or_basicauth()
def listing(request):
    """
    Default index page
    """
    cat = get_relais_categories()

    ind = Individual.objects
    team = Team.objects

    to_template = {
        'cat': cat,
        'individual': ind.all(),
        'team': team.all(),
    }

    return render(request, 'management/listing.html', to_template)

#------------------------------------------------------------------------------
@logged_in_or_basicauth()
def results(request):
    """
    Default index page
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
def results_individual(request):
    """
    Default index page
    """
    cat = get_relais_categories()

    ind = Individual.objects

    to_template = {
        'cat': cat,
    }

    r = []

    r.append(RESULTS(name="Les 3 premiers hommes - Scratch",
                            results=limit_query(ind.filter(runner__gender=constants.MALE)
                                     .order_by('runner__time'), begin=0, end=3)))
    
    r.append(RESULTS(name="Les 3 premiers femme - Scratch",
                            results=limit_query(ind.filter(runner__gender=constants.FEMALE)
                                     .order_by('runner__time'), begin=0, end=3)))

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
    for i in ind.all():
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

    for key_gender, name_gender in people.iteritems():
        # exclude 3 first one runners Male / Female
        exclude = limit_query(ind.filter(runner__gender=key_gender)
                                  .order_by('runner__time'), begin=0, end=3)
        for key, data in r_cat.iteritems():
            name = "{category} - {gender}".format(category=data['name'],
                                                  gender=name_gender)
            if data['ffa']:
                # FFA specificities
                hash_cat = cat2hash(key)
                runner_in_category = ffa[hash_cat][key_gender]
                query = ind.filter(id__in=runner_in_category).exclude(pk__in=exclude).order_by('runner__time')
            else:
                # Relais specificities
                # No exclusion for Relais specificities (cumul)
                query = ind.filter(category=key).order_by('runner__time')
            # get results
            results = limit_query(query, begin=0, end=1)
            r.append(RESULTS(name=name, results=results))
    
    r.append(RESULTS(name="La tenue originale (non géré automatiquement)",
                            results=[]))

    r.append(RESULTS(name="Le dernier",
                            results=limit_query(ind.order_by('-runner__time'), begin=0, end=1)))

    to_template['individual'] = r

    return render(request, 'management/results.html', to_template)

#------------------------------------------------------------------------------
@logged_in_or_basicauth()
def results_team(request):
    """
    Default index page
    """
    cat = get_relais_categories()

    team = Team.objects

    to_template = {
        'cat': cat,
    }
    
    # So... It is quite hard for Team to get results with a good algorithm like
    # as Individual
    # Let's do it manually
    r = []
    # 1) 3 premières équipes M|F
    r.append(RESULTS(name="Equipes Homme",
                            results=limit_query(team.filter(runner_1__gender=constants.MALE,
                                                            runner_2__gender=constants.MALE,
                                                            runner_3__gender=constants.MALE).order_by('runner_3__time'),
                                                begin=0, end=3)))

    r.append(RESULTS(name="Equipes Femme",
                            results=limit_query(team.filter(runner_1__gender=constants.FEMALE,
                                                            runner_2__gender=constants.FEMALE,
                                                            runner_3__gender=constants.FEMALE).order_by('runner_3__time'),
                                                begin=0, end=3)))
    # 2) Première équipe mixte 1
    # Ugly ! :(
    mixte1 = [(constants.FEMALE, constants.MALE, constants.MALE),
               (constants.MALE, constants.FEMALE, constants.MALE),
               (constants.MALE, constants.MALE, constants.FEMALE)]

    q_mixte1 = [Q(runner_1__gender=x[0], runner_2__gender=x[1], runner_3__gender=x[2]) for x in mixte1]

    r.append(RESULTS(name="Equipe mixte 1",
                            results=limit_query(team.filter(reduce(operator.or_, q_mixte1)).order_by('runner_3__time'),
                                                begin=0, end=1)))
    # 3) Premières équipe mixte 2
    # Ugly ! :(
    mixte2 = [(constants.MALE, constants.FEMALE, constants.FEMALE),
               (constants.FEMALE, constants.MALE, constants.FEMALE),
               (constants.FEMALE, constants.FEMALE, constants.MALE)]

    q_mixte2 = [Q(runner_1__gender=x[0], runner_2__gender=x[1], runner_3__gender=x[2]) for x in mixte2]

    r.append(RESULTS(name="Equipe mixte 2",
                            results=limit_query(team.filter(reduce(operator.or_, q_mixte2)).order_by('runner_3__time'),
                                                begin=0, end=1)))

    # 4) Première équipe collégien
    q_college = [Q(runner_1__school__name__icontains=x, runner_2__school__name__icontains=x,
                   runner_3__school__name__icontains=x) for x in ['college', 'collège']]

    r.append(RESULTS(name="Collégiens",
                        results=limit_query(team.filter(category=constants.STUDENT)
                                                 .filter(reduce(operator.or_, q_college)).order_by('runner_3__time'),
                                            begin=0, end=1)))

    # 5) Première équipe lycéen
    q_lycee = [Q(runner_1__school__name__icontains=x, runner_2__school__name__icontains=x,
                   runner_3__school__name__icontains=x) for x in ['lycee', 'lycée']]

    r.append(RESULTS(name="Lycéens",
                        results=limit_query(team.filter(category=constants.STUDENT)
                                                .filter(reduce(operator.or_, q_lycee)).order_by('runner_3__time'),
                                            begin=0, end=1)))

    # 6) Première équipe etudiant M|F
    student = {}
    student['male'] = limit_query(team.filter(Q(category=constants.STUDENT) |
                                                            Q(category=constants.STUDENT_ENSIL))
                                                    .filter(runner_1__gender=constants.MALE,
                                                            runner_2__gender=constants.MALE,
                                                            runner_3__gender=constants.MALE)
                                                    .exclude(reduce(operator.or_, q_college))  # exclude college
                                                    .exclude(reduce(operator.or_, q_lycee))  # exclude lycee
                                                    .order_by('runner_3__time'),
                                                begin=0, end=1)
    r.append(RESULTS(name="Etudiants - Homme",
                            results=student['male']))

    student['female'] = limit_query(team.filter(Q(category=constants.STUDENT) |
                                                            Q(category=constants.STUDENT_ENSIL))
                                                    .filter(runner_1__gender=constants.FEMALE,
                                                            runner_2__gender=constants.FEMALE,
                                                            runner_3__gender=constants.FEMALE)
                                                    .exclude(reduce(operator.or_, q_college))  # exclude college
                                                    .exclude(reduce(operator.or_, q_lycee))  # exclude lycee.order_by('runner_3__time'),
                                                .order_by('runner_3__time'),
                                                begin=0, end=1)

    r.append(RESULTS(name="Etudiants - Femme",
                            results=student['female']))

    # 7) Première équipe etudiant mixte
    q_mixte = [Q(runner_1__gender=x, runner_2__gender=x, runner_3__gender=x) for x in [constants.MALE, constants.FEMALE]]

    student['mix'] = limit_query(team.filter(Q(category=constants.STUDENT) |
                                                        Q(category=constants.STUDENT_ENSIL))
                                                .exclude(reduce(operator.or_, q_mixte))  # exlude M/M/M or F/F/F
                                                .exclude(reduce(operator.or_, q_college))  # exclude college
                                                .exclude(reduce(operator.or_, q_lycee))  # exclude lycee.order_by('runner_3__time'),
                                            .order_by('runner_3__time'),
                                            begin=0, end=1)
    r.append(RESULTS(name="Etudiants - Mixte",
                        results=student['mix']))

    # 8) Première équipe ENSIL M|F
    r.append(RESULTS(name="ENSIL - Homme",
                    results=limit_query(team.filter(category=constants.STUDENT_ENSIL)
                                            .filter(runner_1__gender=constants.MALE,
                                                    runner_2__gender=constants.MALE,
                                                    runner_3__gender=constants.MALE)
                                            .exclude(pk__in=student['male'])
                                            .order_by('runner_3__time'),
                                        begin=0, end=1)))

    r.append(RESULTS(name="ENSIL - Femme",
                    results=limit_query(team.filter(category=constants.STUDENT_ENSIL)
                                            .filter(runner_1__gender=constants.FEMALE,
                                                    runner_2__gender=constants.FEMALE,
                                                    runner_3__gender=constants.FEMALE)
                                            .exclude(pk__in=student['female'])
                                            .order_by('runner_3__time'),
                                        begin=0, end=1)))
    # 9) Première équipe ENSIL mixte
    r.append(RESULTS(name="ENSIL - Mixte",
                    results=limit_query(team.filter(category=constants.STUDENT_ENSIL)
                                            .exclude(reduce(operator.or_, q_mixte))  # exlude M/M/M or F/F/F
                                            .exclude(pk__in=student['mix'])
                                            .order_by('runner_3__time'),
                                        begin=0, end=1)))

    # 10) Première équipe challenge M|F
    r.append(RESULTS(name="Challenge Entreprise - Homme",
                        results=limit_query(team.filter(category=constants.CHALLENGE)
                                                .filter(runner_1__gender=constants.MALE,
                                                        runner_2__gender=constants.MALE,
                                                        runner_3__gender=constants.MALE)
                                                .order_by('runner_3__time'),
                                            begin=0, end=1)))

    r.append(RESULTS(name="Challenge Entreprise - Femme",
                        results=limit_query(team.filter(category=constants.CHALLENGE)
                                                .filter(runner_1__gender=constants.FEMALE,
                                                        runner_2__gender=constants.FEMALE,
                                                        runner_3__gender=constants.FEMALE)
                                                .order_by('runner_3__time'),
                                            begin=0, end=1)))

    # 11) Première équipe challenge mixte
    r.append(RESULTS(name="Challenge Entreprise - Mixte",
                        results=limit_query(team.filter(category=constants.CHALLENGE)
                                                .exclude(reduce(operator.or_, q_mixte))  # exlude M/M/M or F/F/F
                                            .order_by('runner_3__time'),
                                            begin=0, end=1)))

    # 12) Première équipe d'anciens ENSILiens
    r.append(RESULTS(name="Anciens ENSIL",
                            results=limit_query(team.filter(category=constants.OLDER_ENSIL).order_by('runner_3__time'),
                                                begin=0, end=1)))

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

def status(request):
    runners = Runner.objects
    # list all tshirts size
    tshirt = {}
    first = runners.order_by('id')[0:150]
    for s in TSHIRT_CHOICES:
        tshirt[s[0]] = len(runners.filter(tshirt=s[0], pk__in=first))
    canicross = len(runners.filter(canicross=True))
    nb_runners = len(runners.objects.all())
    return render(request)
