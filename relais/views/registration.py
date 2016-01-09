from django.core.mail.message import EmailMessage
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.template import loader
from django.template.base import Template
from django.template.context import Context

from engine.settings.production import DEVELOPPER_MAIL
from relais import constants, forms, models, helpers
from relais.constants import RANGE_INDIVIDUAL, RANGE_TEAM
from relais.models import (
    Individual,
    Payment,
    Price,
    Runner,
    Setting,
    Team,
)
from relais.util.decorator import registration_opened
from relais.views.payment import sendmail_payment_pending


#------------------------------------------------------------------------------
def sendmail_summary(payment):
    setting = Setting.objects.get()
    # XXX: find another way to do this !
    category = {}
    for i, name in models.CATEGORY_CHOICES:
        category[i] = name
    context = {'setting': setting, 'category': category}
    try:
        context['team'] = payment.team
        to = payment.team.email
        msg = loader.render_to_string('registration/mail/team.rst', context)
    except Team.DoesNotExist:
        context['individual'] = payment.individual
        to = payment.individual.email
        msg = loader.render_to_string('registration/mail/individual.rst', context)

    mail = EmailMessage('[Relais de l\'ENSIL] - Confirmation inscription', msg,
                        setting.email, [to], [setting.email, DEVELOPPER_MAIL])
    mail.send(fail_silently=False)

#------------------------------------------------------------------------------
@registration_opened()
def index(request):
    """
    Default index page
    """
    # delete the session if exists
    try:
        del request.session['accept-rules']
    except KeyError:
        pass

    # by default, 1 setting object is in database
    settings = Setting.objects.get()

    # update rule from database
    rule = Template(settings.rule)
    a = Context(settings.__dict__)
    a['edition_nb'] = settings.get_edition_nb()  # see method in models.py
    settings.rule = rule.render(a)  # convert {} with desired data

    # aggregate to dict
    # XXX: find another way to do this !
    # format-like
    #     prices = {
    #         'ONLINE': {
    #             'ADULT': {
    #                 'INDIVIDUAL': '5',
    #                 'TEAM': '10',
    #             },
    #             'STUDENT': {
    #                 'INDIVIDUAL': '0',
    #                 'TEAM': '0',
    #             }
    #             ...
    #         }
    #        ...
    #     }
    prices = {}
    for w, _ in models.WHEN_CHOICES:
        prices[w] = {}
        for c, _ in models.CATEGORY_CHOICES:
            prices[w][c] = {}
            for r, _ in models.CONFIG_CHOICES:
                try:
                    p = Price.objects.filter(when=w, who=c, config=r).get()
                    prices[w][c][r] = p.price
                except:
                    prices[w][c][r] = 'N/A'

    # create form for Rules, or populate it from POST request
    rule_form = forms.RulesForm(request.POST or None)
    if request.method == 'POST':
        if rule_form.is_valid():
            # set session (all users must accept rules)
            request.session['accept-rules'] = True
            return HttpResponseRedirect('/registration/category/')

    # create dict for template
    data = {
        'settings': settings,
        'categories': models.CATEGORY_CHOICES,
        'prices': prices,
        'constants': constants,
        'form': rule_form,
    }

    return render(request, 'registration/home.html', data)

#------------------------------------------------------------------------------
@registration_opened()
def category(request):
    """
    User has to choose in which category he wants to run
    """
    # No session detected => No rules accepted. Let's redirect.
    if not request.session.get('accept-rules', False):
        return HttpResponseRedirect('/registration')

    # create a new form to choose the category, or complete it
    form = forms.ConfigForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            # redirect if user choose individual
            if form.cleaned_data['choice'] == constants.INDIVIDUAL:
                return HttpResponseRedirect('/registration/category/individual')

            # redirect if user choose team
            elif form.cleaned_data['choice'] == constants.TEAM:
                return HttpResponseRedirect('/registration/category/team')

    # default page if no category has been choosen
    return render(request, 'registration/category.html', {'form': form})

#------------------------------------------------------------------------------
@registration_opened()
def individual(request):
    """
    Display form for individual choose
    """
    # No session detected => No rules accepted. Let's redirect.
    if not request.session.get('accept-rules', False):
        return HttpResponseRedirect('/registration')

    # create a new form for individual information, or complete it
    form = forms.IndividualForm(request.POST or None)

    # get all data from the database to autocomplete some fields
    autocomplete = helpers.get_all_autocomplete()

    if request.method == 'POST':
        if form.is_valid():
            # extra operation for club/federation/school/company
            # are already done by IndividualForm.clean

            # add runner (it is safe now)
            r = Runner(first_name=form.cleaned_data['first_name'],
                       last_name=form.cleaned_data['last_name'],
                       gender=form.cleaned_data['gender'],
                       birthday=form.cleaned_data['birthday'],
                       license_nb=form.cleaned_data['license'],
                       school=form.cleaned_data['school'],
                       federation=form.cleaned_data['federation'],
                       club=form.cleaned_data['club'],
                       canicross=form.cleaned_data['canicross'],
                       certificat=False,
                       legal_status=form.cleaned_data['legal_status'],
                       tshirt=form.cleaned_data['tshirt'])
            r.update_num(RANGE_INDIVIDUAL)
            r.clean()
            r.save()

            # get online price for desired category
            p = Price.objects.filter(when=constants.PRICE_ONLINE,
                                     config=constants.INDIVIDUAL,
                                     who=form.cleaned_data['category']).get()

            if p.price == 0:
                # TODO: atomic transation
                # free registration: add cash payment
                pay = Payment.objects.create(price=p,
                                             method=constants.CASH,
                                             state=True)
            else:
                pay = Payment.objects.create(price=p,
                                             method=constants.UNKNOWN,
                                             state=False)
            # add individual
            Individual.objects.create(runner=r,
                                      payment=pay,
                                      category=form.cleaned_data['category'],
                                      email=form.cleaned_data['email'],
                                      company=form.cleaned_data['company'])
            sendmail_summary(payment=pay)
            if p.price == 0:
                # end of registration
                return HttpResponseRedirect('/registration/done')
            else:
                sendmail_payment_pending(payment=pay)
                # redirect to payment page
                return HttpResponseRedirect('/payment/%s/%s' % (pay.id, pay.token))

    # if any error or no data, display page
    return render(request, 'registration/individual.html', {'form': form,
                                                            'autocomplete': autocomplete})

#------------------------------------------------------------------------------
@registration_opened()
def team(request):
    """
    Display form for team choose
    """
    # No session detected => No rules accepted. Let's redirect.
    if not request.session.get('accept-rules', False):
        return HttpResponseRedirect('/registration')

    # create a new form for individual information, or complete it
    form = forms.TeamForm(request.POST or None)

    # get all data from the database to autocomplete some fields
    autocomplete = helpers.get_all_autocomplete()

    if request.method == 'POST':
        if form.is_valid():
            # extra operation for club/federation/school/company
            # are already done by IndividualForm.clean

            # add runners (it is safe now)
            r = {}
            for i in xrange(1, 4):
                r[i] = Runner(first_name=form.cleaned_data['first_name_%d' % i],
                              last_name=form.cleaned_data['last_name_%d' % i],
                              gender=form.cleaned_data['gender_%d' % i],
                              birthday=form.cleaned_data['birthday_%d' % i],
                              license_nb=form.cleaned_data['license_%d' % i],
                              school=form.cleaned_data['school'],
                              federation=form.cleaned_data['federation_%d' % i],
                              club=form.cleaned_data['club_%d' % i],
                              canicross=form.cleaned_data['canicross'],
                              certificat=False,
                              legal_status=form.cleaned_data['legal_status_%d' % i],
                              tshirt=form.cleaned_data['tshirt_%d' % i])
                r[i].update_num(RANGE_TEAM[i])
                r[i].clean()
                r[i].save()

            # get online price for desired category
            p = Price.objects.filter(when=constants.PRICE_ONLINE,
                                     config=constants.TEAM,
                                     who=form.cleaned_data['category']).get()

            if p.price == 0:
                # TODO: atomic transaction
                # free registration: add cash payment
                pay = Payment.objects.create(price=p,
                                             method=constants.CASH,
                                             state=True)
            else:
                pay = Payment.objects.create(price=p,
                                             method=constants.UNKNOWN,
                                             state=False)
            # add team
            Team.objects.create(runner_1=r[1], runner_2=r[2], runner_3=r[3],
                                payment=pay,
                                name=form.cleaned_data['name'],
                                category=form.cleaned_data['category'],
                                email=form.cleaned_data['email'],
                                company=form.cleaned_data['company'])

            # Send mail to team
            sendmail_summary(payment=pay)
            # Send mail about payment if any (before redirect)
            if not pay.state:
                sendmail_payment_pending(payment=pay)
            # redirect to payment page
            return HttpResponseRedirect('/payment/%s/%s' % (pay.id, pay.token))

    # if this is a POST request we need to process the form data
    return render(request, 'registration/team.html', {'form': form,
                                                      'autocomplete': autocomplete})
