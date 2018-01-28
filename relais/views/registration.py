from django.contrib.auth.decorators import login_required
from django.core.mail.message import EmailMessage
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.template import loader
from django.template.base import Template
from django.template.context import Context
from django.utils.crypto import get_random_string

from engine.settings.production import DEVELOPPER_MAIL
from relais import constants, forms, models, helpers
from relais.models import (
    Payment,
    People,
    Price,
    Runner,
    Setting,
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
    context['r'] = payment.runner
    to = payment.runner.email
    if payment.runner.team:
        msg = loader.render_to_string('registration/mail/team.rst', context).replace("&#39;","'")
    else:
        msg = loader.render_to_string('registration/mail/individual.rst', context).replace("&#39;","'")

    mail = EmailMessage('[Relais de l\'ENSIL-ENSCI] - Confirmation inscription', msg,
                        setting.email, [to], [setting.email, DEVELOPPER_MAIL])
    mail.send(fail_silently=True)

@registration_opened()
def online(*args, **kwargs):
    func = kwargs.pop('func')
    return func(onsite=False, prefix='', *args, **kwargs)

@login_required
def onsite(*args, **kwargs):
    func = kwargs.pop('func')
    return func(onsite=True, prefix='/management', *args, **kwargs)

#------------------------------------------------------------------------------
def index(request, prefix='', onsite=False):
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
            return HttpResponseRedirect('%s/registration/category/' % prefix)

    # create dict for template
    data = {
        'settings': settings,
        'categories': models.CATEGORY_CHOICES,
        'prices': prices,
        'constants': constants,
        'form': rule_form,
        'prefix': prefix,
    }

    return render(request, 'registration/home.html', data)

#------------------------------------------------------------------------------
def category(request, prefix='', onsite=False):
    """
    User has to choose in which category he wants to run
    """

    # No session detected => No rules accepted. Let's redirect.
    if not request.session.get('accept-rules', False):
        return HttpResponseRedirect('%s/registration' % prefix)

    # create a new form to choose the category, or complete it
    form = forms.ConfigForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            # redirect if user choose individual
            if form.cleaned_data['choice'] == constants.INDIVIDUAL:
                return HttpResponseRedirect('%s/registration/category/individual' % prefix)

            # redirect if user choose team
            elif form.cleaned_data['choice'] == constants.TEAM:
                return HttpResponseRedirect('%s/registration/category/team' % prefix)

    # default page if no category has been choosen
    return render(request, 'registration/category.html', {'form': form, 'prefix': prefix})

#------------------------------------------------------------------------------
def form(request, prefix='', team=False, onsite=False):
    """
    Display form for individual/team choose
    """

    # No session detected => No rules accepted. Let's redirect.
    if not request.session.get('accept-rules', False):
        return HttpResponseRedirect('%s/registration' % prefix)

    # create a new form for individual information, or complete it
    form = forms.SubscriptionForm(request.POST or None, is_a_team=team, onsite=onsite)

    # get all data from the database to autocomplete some fields
    autocomplete = helpers.get_all_autocomplete()

    if request.method == 'POST':
        if form.is_valid():
            # extra operation for club/federation/school/company
            # are already done by IndividualForm.clean
            if team:
                config = constants.TEAM
            else:
                config = constants.INDIVIDUAL

            if onsite:
                price = constants.PRICE_DAY
                pay_method = constants.CASH
                pay_status = True
            else:
                price = constants.PRICE_ONLINE
                pay_method = constants.UNKNOWN
                pay_status = False

            # add runners (it is safe now)
            r = [None] * 3
            for i in range(form.nb):
                r[i] = People(first_name=form.cleaned_data['first_name_%d' % i],
                              last_name=form.cleaned_data['last_name_%d' % i],
                              num=form.cleaned_data['num_%d' % i],
                              gender=form.cleaned_data['gender_%d' % i],
                              birthday=form.cleaned_data['birthday_%d' % i],
                              license_nb=form.cleaned_data['license_%d' % i],
                              school=form.cleaned_data['school'],
                              federation=form.cleaned_data['federation_%d' % i],
                              club=form.cleaned_data['club_%d' % i],
                              certificat=False,
                              legal_status=form.cleaned_data['legal_status_%d' % i],
                              tshirt=form.cleaned_data['tshirt_%d' % i])
                r[i].clean()
                r[i].save()

            # get online price for desired category
            p = Price.objects.filter(when=price,
                                     config=config,
                                     who=form.cleaned_data['category']).get()
            token = get_random_string()
            if p.price == 0:
                # TODO: atomic transaction
                # free registration: add cash payment
                pay = Payment.objects.create(price=p,
                                             method=constants.CASH,
                                             token=token,
                                             state=True)
            else:
                pay = Payment.objects.create(price=p,
                                             method=pay_method,
                                             token=token,
                                             state=pay_status)
            registered = Runner.objects.create(
                runner_1=r[0], runner_2=r[1], runner_3=r[2],
                payment=pay,
                team=form.cleaned_data.get('name', None),
                category=form.cleaned_data['category'],
                email=form.cleaned_data['email'],
                company=form.cleaned_data['company']
            )

            if team and onsite:
                return HttpResponseRedirect('/management/registration/end/team/%s' % registered.pk)
            elif not team and onsite:
                return HttpResponseRedirect('/management/registration/end/indiv/%s' % registered.pk)

            # Send mail
            sendmail_summary(payment=pay)
            # Send mail about payment if any (before redirect)
            if not pay.state:
                sendmail_payment_pending(payment=pay)
            # redirect to payment page
            return HttpResponseRedirect('/payment/%s/%s' % (pay.id, pay.token))

    # if this is a POST request we need to process the form data
    return render(request, 'registration/%s.html' % ('team' if team else 'individual'),
                  {'form': form, 'autocomplete': autocomplete,  'prefix': prefix})

#------------------------------------------------------------------------------
def end(request, category, pk, prefix='', onsite=False):
    r = Runner.objects.filter(pk=pk).get()
    if category == 'indiv':
        return render(request, 'registration/end_indiv.html', {'indiv': r})

    elif category == 'team':
        return render(request, 'registration/end_team.html', {'team': r})
