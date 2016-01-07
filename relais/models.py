#-*-coding: utf-8 -*-
import datetime

from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
from django.db import models
from django.utils.crypto import get_random_string
from django.utils.translation import ugettext as _
from paypal.standard.ipn.models import PayPalIPN

from relais import constants


#------------------------------------------------------------------------------
class Setting(models.Model):
    """
    Configuration of the event
    """
    email = models.EmailField(_('Email'))
    email_contact = models.EmailField(_('Email contact'))
    url = models.URLField(_('URL to registration'))
    url_home = models.URLField(_('URL to home'))
    phone = models.CharField(_('Phone'), max_length=14)
    first_event = models.DateTimeField(_('First event'))
    event = models.DateTimeField(_('Event'))
    closure_postal = models.DateTimeField(_('End of postal subscription'))
    open_online = models.DateTimeField(_('Open of online subscription'))
    closure_online = models.DateTimeField(_('End of online subscription'))
    rule = models.TextField(_('Legacy rules'))
    disclamer = models.TextField(_('Disclamer'))
    postal_address = models.TextField(_('Postal address'))

    class Meta:
        verbose_name = _('Setting')

    def get_edition_nb(self):
        diff = self.event - self.first_event
        return (diff.days / 365) + 1

#------------------------------------------------------------------------------
CATEGORY_CHOICES = ((constants.ADULT, _('Adult')),
                    (constants.STUDENT, _('Student')),
                    (constants.STUDENT_ENSIL, _('Student ENSIL')),
                    (constants.CHALLENGE, _('Challenge company')),
                    (constants.OLDER_ENSIL, _('Old ENSIL people')))

WHEN_CHOICES = ((constants.PRICE_ONLINE, _('Online')),
                (constants.PRICE_DAY, _('On-site')))

CONFIG_CHOICES = ((constants.INDIVIDUAL, _('Individual')),
                  (constants.TEAM, _('Team of 3 people')))

class Price(models.Model):
    """
    Price of each category.
    """
    config = models.CharField(_('Type of runner'), max_length=5, choices=CONFIG_CHOICES)
    who = models.CharField(_('Category of runner'), max_length=5, choices=CATEGORY_CHOICES)
    when = models.CharField(_('When'), max_length=5, choices=WHEN_CHOICES)
    price = models.IntegerField(_('Price'))

    class Meta:
        """
        Additional informations
        """
        verbose_name = _('Price')
        verbose_name_plural = _('Prices')
        unique_together = ('config', 'who', 'when')  # one price is allowed

    def __unicode__(self):
        return u'%s %s (%s) - %s €' % (self.get_config_display(), self.get_who_display(),
                                       self.get_when_display(), self.price)

#------------------------------------------------------------------------------
class Federation(models.Model):
    name = models.CharField(_('Name'), max_length=30)

    class Meta:
        verbose_name = _('Federation')

    def __unicode__(self):
        return u'%s' % self.name

#------------------------------------------------------------------------------
class Company(models.Model):
    name = models.CharField(_('Name'), max_length=30)

    class Meta:
        verbose_name = _('Company')

    def __unicode__(self):
        return u'%s' % self.name

#------------------------------------------------------------------------------
class Club(models.Model):
    name = models.CharField(_('Name'), max_length=30)

    class Meta:
        verbose_name = _('Club')

    def __unicode__(self):
        return u'%s' % self.name

#------------------------------------------------------------------------------
class School(models.Model):
    name = models.CharField(_('Name'), max_length=30)

    class Meta:
        verbose_name = _('School')

    def __unicode__(self):
        return u"%s" % self.name

#------------------------------------------------------------------------------
METHOD_PAYMENT_CHOICES = ((constants.CASH, _('Cash')),
                          (constants.CHEQUE, _('Cheque')),
                          (constants.PAYPAL, u'Paypal'),
                          (constants.UNKNOWN, _('Unknown')))

class Payment(models.Model):
    """
    All payments (Individual / Team) are stored in this model.
    """
    # Relation between Payment.price <-> Price
    price = models.ForeignKey(Price, verbose_name=_('Price'))
    method = models.CharField(_('Method'), max_length=3, choices=METHOD_PAYMENT_CHOICES)
    state = models.BooleanField(_('Validate'))
    token = models.CharField('Token', max_length=30, default=get_random_string(),
                             editable=False)
    # TODO: update at each action
    time = models.DateTimeField(auto_now=True)
    # For PayPal only
    ipn = models.ForeignKey(PayPalIPN, blank=True, null=True)

    class Meta:
        verbose_name = _('Payment')

    def __unicode__(self):
        if self.state:
            s = _('approved')
        else:
            s = _('under validation')
        return u'ID: %d - %s (%s) %s' % (self.id, self.price, self.get_method_display(), s)

#------------------------------------------------------------------------------
GENDER_CHOICES = ((constants.MALE, _('Male')),
                  (constants.FEMALE, _('Female')))

class Runner(models.Model):
    """
    List of people that will run for this event.
    """
    first_name = models.CharField(_('First name'), max_length=30)
    last_name = models.CharField(_('Last name'), max_length=30)
    gender = models.CharField(_('Gender'), max_length=1, choices=GENDER_CHOICES)
    birthday = models.DateField(_('Birthday'))

    # additional informations (can be null and blank)
    # some items have a relation with other models.
    license_nb = models.CharField(_('License number'), max_length=30, blank=True, null=True)
    school = models.ForeignKey(School, verbose_name=_('School'), blank=True, null=True)
    federation = models.ForeignKey(Federation, verbose_name=_('Federation'), blank=True, null=True)
    company = models.ForeignKey(Company, verbose_name=_('Company'), blank=True, null=True)
    club = models.ForeignKey(Club, verbose_name=_('Club'), blank=True, null=True)

    # for the management
    certificat = models.BooleanField(_('Medical certification'))
    legal_status = models.BooleanField(_('Legal status'))  # for minor
    num = models.PositiveIntegerField(_('Bib Number'), unique=True)
    time = models.TimeField(_('Time'), blank=True, null=True)
    ready = models.BooleanField(_('Ready to run'), default=False)

    def age(self):
        today = datetime.date.today()
        num_years = int((today - self.birthday).days / 365.2425)
        return num_years

    def runner_categogy(self):
        """
        Category are given by FF(?)
        """
        age = self.age()
        if age <= 9:
            r = constants.POUSSIN
        elif 10 <= age and age <= 11:
            r = constants.PUPILLE
        elif 12 <= age and age <= 13:
            r = constants.BENJAMIN
        elif 14 <= age and age <= 15:
            r = constants.MINIME
        elif 16 <= age and age <= 17:
            r = constants.CADET
        elif 18 <= age and age <= 19:
            r = constants.JUNIOR
        elif 20 <= age and age <= 22:
            r = constants.ESPOIR
        elif 23 <= age and age <= 39:
            r = constants.SENOIR
        elif 40 <= age and age <= 49:
            r = constants.V1
        elif 50 <= age and age <= 59:
            r = constants.V2
        elif 60 <= age and age <= 69:
            r = constants.V3
        else:
            r = constants.V4

        return r

    def can_run(self):
        """
        According to FF (?), a runner cannot have less than 14 yo.
        """
        age = self.age()
        # TODO: can be manageable
        if age < 14:
            return False
        else:
            return True

    def is_minor(self):
        """
        TODO
        """
        age = self.age()
        # TODO: can be manageable
        if age < 18:
            return True
        else:
            return False

    def clean(self):
        """
        Update bib number if not exist
        Check if runner can run
        """
        if not self.num:
            # get last bib number and incremente id
            # if not exist, force to 100
            # TODO: can be manageable
            try:
                query = Runner.objects.latest(field_name='id')
                self.num = query.num + 1
            except models.exceptions.ObjectDoesNotExist:
                self.num = 100

        if not self.can_run():
            # raise an error and avoid registration
            # TODO: translation
            raise ValidationError(
                {
                    NON_FIELD_ERRORS: [
                        u'%s ne peut pas s\'inscrire, l\'âge minimale est de '
                        u'14 ans, ce dernier ayant %s ans.' % (self, self.age())
                    ],
                }
            )

    class Meta:
        verbose_name = _('Runner')
        # unicity of Runner, avoid duplication
        unique_together = ('first_name', 'last_name', 'birthday', 'gender')

    def __unicode__(self):
        return u'%s %s (%d)' % (self.first_name, self.last_name, self.num)

#------------------------------------------------------------------------------
class Individual(models.Model):
    """
    Runner alone who runs the full circuit.
    """
    # One Individual -> One Runner (unicity)
    runner = models.OneToOneField(Runner, verbose_name=_('Runner'))
    email = models.EmailField(_('Email'))
    category = models.CharField(_('Category of runner'), max_length=3, choices=CATEGORY_CHOICES)
    # One Individual -> One payment (unicity)
    payment = models.OneToOneField(Payment, verbose_name=_('Payment'))

    # Additional information
    company = models.ForeignKey(Company, verbose_name=_('Company'), blank=True, null=True)

    def can_run(self):
        """
        According to FF(?), to run 10 km, runner must have more than 16 yo.
        """
        if self.runner.age() < 16:
            return False
        else:
            return True

    def clean(self):
        """
        Check if Individual can run
        """
        if not self.can_run():
            raise ValidationError(
                {
                    NON_FIELD_ERRORS: [
                        u'%s ne peut pas s\'inscrire en individuel, l\'âge '
                        u'minimal est de 16 ans, ce dernier ayant %s ans.'
                        % (self.runner, self.runner.age())
                    ],
                }
            )

    def validate_unique(self, exclude=None, *args, **kwargs):
        """
        Check if Runner is not in another Individual or Team
        The OneToOne relation is only available between two tables,
        not between three tables.
        """
        super(Individual, self).validate_unique(*args, **kwargs)
        if self.runner:
            team = None
            if Team.objects.filter(runner_1=self.runner).exists():
                team = Team.objects.filter(runner_1=self.runner).get()
            elif Team.objects.filter(runner_2=self.runner).exists():
                team = Team.objects.filter(runner_2=self.runner).get()
            elif Team.objects.filter(runner_3=self.runner).exists():
                team = Team.objects.filter(runner_3=self.runner).get()
            if team:
                raise ValidationError(
                    {
                        # TODO: translation
                        NON_FIELD_ERRORS: [
                            u'%s est déjà dans une équipe (%s)' % (self.runner, team)
                        ],
                    }
                )

    def delete(self, *args, **kwargs):
        """
        When deleting a Individual, delete all related objects.
        """
        self.runner.delete()
        self.payment.delete()
        super(Individual, self).delete(*args, **kwargs)  # Call the "real" delete() method.

    class Meta:
        verbose_name = _('Individual')

    def __unicode__(self):
        return u'%s' % self.runner

#------------------------------------------------------------------------------
class Team(models.Model):
    """
    A Team is composed by 3 runners.
    """
    name = models.CharField('Name', max_length=30)
    email = models.EmailField(_('Email'))  # useful ?
    category = models.CharField(_('Category of runner'), max_length=3, choices=CATEGORY_CHOICES)
    # OneToOne relation between Runner and Team
    runner_1 = models.OneToOneField(Runner, verbose_name=_('1st runner'),
                                    related_name='team_runner_1')
    runner_2 = models.OneToOneField(Runner, verbose_name=_('2nd runner'),
                                    related_name='team_runner_2')
    runner_3 = models.OneToOneField(Runner, verbose_name=_('3rd runner'),
                                    related_name='team_runner_3')
    company = models.ForeignKey(Company, verbose_name=_('Company'), blank=True, null=True)
    # OneToOne relation between Payment and Team
    payment = models.OneToOneField(Payment, verbose_name=_('Payment'))

    def validate_unique(self, exclude=None, *args, **kwargs):
        """
        Check if all Runner are not in Individual
        """
        super(Team, self).validate_unique(*args, **kwargs)
        for runner in [self.runner_1, self.runner_2, self.runner_3]:
            if Individual.objects.filter(runner=runner).exists():
                raise ValidationError(
                    {
                        # TODO: translation
                        NON_FIELD_ERRORS: [
                            u'Le coureur %s est déjà inscrit en individuel' % runner,
                        ],
                    }
                )

    def delete(self, *args, **kwargs):
        """
        When deleting a Team, delete all related objects.
        """
        self.runner_1.delete()
        self.runner_2.delete()
        self.runner_3.delete()
        self.payment.delete()
        super(Team, self).delete(*args, **kwargs)

    class Meta:
        verbose_name = _('Team')

    def __unicode__(self):
        return u'%s' % self.name
