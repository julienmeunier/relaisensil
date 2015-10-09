import json

from django.core.mail.message import EmailMessage
from django.shortcuts import render
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
from django.views.defaults import page_not_found
from paypal.standard.forms import PayPalPaymentsForm
from paypal.standard.ipn.signals import valid_ipn_received, invalid_ipn_received
from paypal.standard.models import ST_PP_COMPLETED

from engine.settings import production as settings
from engine.settings.production import DEVELOPPER_MAIL
from relais import constants
from relais import forms
from relais.forms import PaymentForm
from relais.models import Payment, Setting, Team


#------------------------------------------------------------------------------
def sendmail_payment_success(payment):
    setting = Setting.objects.get()
    context = {'setting': setting, 'payment': payment}
    try:
        context['name'] = payment.team
        to = payment.team.email
    except Team.DoesNotExist:
        context['name'] = payment.individual
        to = payment.individual.email
    msg = loader.render_to_string('payment/mail/success.rst', context)
    mail = EmailMessage('[Relais de l\'ENSIL] - Paiement valide', msg, setting.email,
                        [to], [setting.email, DEVELOPPER_MAIL])
    mail.send(fail_silently=True)

#------------------------------------------------------------------------------
def sendmail_payment_pending(payment):
    setting = Setting.objects.get()
    context = {'setting': setting, 'payment': payment}
    try:
        context['name'] = payment.team
        to = payment.team.email
    except Team.DoesNotExist:
        context['name'] = payment.individual
        to = payment.individual.email
    msg = loader.render_to_string('payment/mail/pending.rst', context)

    mail = EmailMessage('[Relais de l\'ENSIL] - Paiement en attente', msg, setting.email,
                        [to], [setting.email, DEVELOPPER_MAIL])
    mail.send(fail_silently=True)

#------------------------------------------------------------------------------
def sendmail_payment_postal(payment):
    setting = Setting.objects.get()
    context = {'setting': setting, 'payment': payment}
    try:
        context['name'] = payment.team
        to = payment.team.email
    except Team.DoesNotExist:
        context['name'] = payment.individual
        to = payment.individual.email
    msg = loader.render_to_string('payment/mail/postal.rst', context)

    mail = EmailMessage('[Relais de l\'ENSIL] - Paiement en attente', msg, setting.email,
                        [to], [setting.email, DEVELOPPER_MAIL])
    mail.send(fail_silently=True)

#------------------------------------------------------------------------------
# on return page, paypal has not csrf token. disable this checking
@csrf_exempt
def update_method(request, idpay, token):
    # get valid Payment
    try:
        pay = Payment.objects.filter(id=idpay, token=token).get()
        setting = Setting.objects.get()
        context = {'payment': pay, 'setting': setting}
    except Payment.DoesNotExist:
        return page_not_found(request)

    if not pay.state:
        form = PaymentForm(request.POST or None)
        # if this is a POST request we need to process the form data
        if request.method == 'POST':
            form = forms.PaymentForm(request.POST or None)
            if form.is_valid():
                pay.method = form.cleaned_data['method']
                pay.save()
                # Paypal
                if form.cleaned_data['method'] == constants.PAYPAL:
                    current_site = Setting.objects.get().url
                    # TODO: URL
                    # Create Paypal button
                    paypal_dict = {
                        'business': settings.PAYPAL_RECEIVER_EMAIL,
                        'amount': pay.price.price,
                        'item_name': str(pay.price),
                        'invoice': '%s-%s' % (idpay, token),
                        'lc': 'FR',
                        'currency_code': 'EUR',
                        'custom': json.dumps({'id': idpay, 'token': token}),  # id and token are given to paypal
                        'notify_url': current_site + '/paypal/',
                        'return_url': current_site + '/payment/%s/%s' % (idpay, token),
                        'cancel_return': current_site + '/payment/%s/%s' % (idpay, token),
                    }
                    # Create the instance.
                    form = PayPalPaymentsForm(initial=paypal_dict)
                    return render(request, 'payment/paypal.html', {'form': form})

                # Cheque
                elif form.cleaned_data['method'] == constants.CHEQUE:
                    sendmail_payment_postal(pay)
                    return render(request, 'payment/postal.html', context)

                # Espece
                else:
                    sendmail_payment_postal(pay)
                    return render(request, 'payment/postal.html', context)
                return render(request, 'payment/done.html', context)

        # Create the instance.
        context['form'] = PaymentForm(request.POST or None)
        context['display_form'] = pay.method == constants.UNKNOWN
        return render(request, 'payment/method.html', context)

    else:
        return render(request, 'payment/done.html', context)

#------------------------------------------------------------------------------
def update_paypal(sender, **kwargs):
    """
    Method called when a IPN signal has been triggered
    """
    ipn_obj = sender
    try:
        payment = json.loads(ipn_obj.custom)

        # try to get payment. if not exist, exception will be catched
        p = Payment.objects.filter(id=payment.get('id'), token=payment.get('token')).get()

        # update payment
        p.method = constants.PAYPAL
        p.ipn = ipn_obj
        p.save()

        # if payment is completed, so valid
        if ipn_obj.payment_status == ST_PP_COMPLETED:
            # check correct price , currency and mail
            if int(ipn_obj.mc_gross) == int(p.price.price) and \
                    ipn_obj.mc_currency == 'EUR' and \
                    ipn_obj.business == settings.PAYPAL_RECEIVER_EMAIL:
                # all is OK, update state
                p.state = True
                p.save()
                sendmail_payment_success(p)
        else:
            # TODO: send alert / mail
            return
    except Payment.DoesNotExist:
        # TODO: send alert / mail
        pass
    except:
        # TODO: send alert / mail
        pass

# See django-paypal API.
# When Paypal sends us a POST request, a signal is sent to all objects
# that are connected
# We want to be informed of any PayPal actions
valid_ipn_received.connect(update_paypal)
invalid_ipn_received.connect(update_paypal)
