import datetime

from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
from django.db import models
from django.utils.crypto import get_random_string
from paypal.standard.ipn.models import PayPalIPN

from relais import constants
from relais.constants import RANGE_INDIVIDUAL, RANGE_TEAM


#------------------------------------------------------------------------------
class Setting(models.Model):
    """
    Configuration of the event
    """
    email = models.EmailField('Email pour inscription')
    email_contact = models.EmailField('Email de contact')
    url = models.URLField('URL du module d\'inscription')
    url_home = models.URLField('URL vers le site')
    phone = models.CharField('Téléphone', max_length=14)
    first_event = models.DateTimeField('Date première édition')
    event = models.DateTimeField('Date de l\'édition')
    closure_postal = models.DateTimeField('Fin des inscriptions par voie postale')
    open_online = models.DateTimeField('Ouverture des inscriptions en ligne')
    closure_online = models.DateTimeField('Fermeture des inscriptions en ligne')
    rule = models.TextField('Règlement')
    disclamer = models.TextField('Décharge de responsabilité')
    postal_address = models.TextField('Adresse postale')
    start = models.DateTimeField('Date et heure du départ de la course',
                                 blank=True, null=True)

    class Meta:
        verbose_name = 'Configuration'

    def get_edition_nb(self):
        diff = self.event - self.first_event
        return int((diff.days / 365) + 1)

#------------------------------------------------------------------------------
CATEGORY_CHOICES = ((constants.ADULT, 'Adulte'),
                    (constants.STUDENT, 'Etudiant'),
                    (constants.STUDENT_ENSIL_ENSCI, 'Etudiant ENSIL-ENSCI'),
                    (constants.CHALLENGE, 'Challenge inter-entreprise'),
                    (constants.OLDER, 'Ancien de l\'ENSIL-ENSCI'))

WHEN_CHOICES = ((constants.PRICE_ONLINE, 'En ligne'),
                (constants.PRICE_DAY, 'Sur place'))

CONFIG_CHOICES = ((constants.INDIVIDUAL, 'Individuel'),
                  (constants.TEAM, 'Equipe de 3 personnes'))

class Price(models.Model):
    """
    Price of each category.
    """
    config = models.CharField('Type de coureur', max_length=12, choices=CONFIG_CHOICES)
    who = models.CharField('Catégorie du coureur', max_length=20, choices=CATEGORY_CHOICES)
    when = models.CharField('Quand', max_length=10, choices=WHEN_CHOICES)
    price = models.IntegerField('Prix')

    class Meta:
        """
        Additional informations
        """
        verbose_name = 'Prix'
        verbose_name_plural = 'Prix'
        unique_together = ('config', 'who', 'when')  # one price is allowed

    def __str__(self):
        return '%s %s (inscription %s) - Montant %s €' % (self.get_config_display(), self.get_who_display(),
                                       self.get_when_display(), self.price)

#------------------------------------------------------------------------------
class Federation(models.Model):
    name = models.CharField('Nom', max_length=30, unique=True)

    class Meta:
        verbose_name = 'Fédération'

    def __str__(self):
        return '%s' % self.name

#------------------------------------------------------------------------------
class Company(models.Model):
    name = models.CharField('Nom', max_length=30, unique=True)

    class Meta:
        verbose_name = 'Entreprise'

    def __str__(self):
        return '%s' % self.name

#------------------------------------------------------------------------------
class Club(models.Model):
    name = models.CharField('Nom', max_length=30, unique=True)

    class Meta:
        verbose_name = 'Club'

    def __str__(self):
        return '%s' % self.name

#------------------------------------------------------------------------------
class School(models.Model):
    name = models.CharField('Nom', max_length=30, unique=True)

    class Meta:
        verbose_name = 'Ecole'

    def __str__(self):
        return "%s" % self.name

#------------------------------------------------------------------------------
METHOD_PAYMENT_CHOICES = ((constants.CASH, 'Espèce'),
                          (constants.CHEQUE, 'Chèque'),
                          (constants.PAYPAL, 'Paypal'),
                          (constants.UNKNOWN, 'Inconnu'))

class Payment(models.Model):
    """
    All payments are stored in this model.
    """
    # Relation between Payment.price <-> Price
    price = models.ForeignKey(Price, verbose_name='Prix')
    method = models.CharField('Méthode', max_length=10, choices=METHOD_PAYMENT_CHOICES)
    state = models.BooleanField('Validé', default=False)
    token = models.CharField('Token', max_length=30, default=get_random_string(),
                             editable=False)
    # TODO: update at each action
    time = models.DateTimeField(auto_now=True)
    # For PayPal only
    ipn = models.ForeignKey(PayPalIPN, blank=True, null=True)

    class Meta:
        verbose_name = 'Paiement'

    def __str__(self):
        if self.state:
            s = 'validé par l\'équipe organisatrice'
        else:
            s = 'en attente de validation par l\'équipe organisatrice' 
        return 'Paiement numéro %d, Catégorie: %s, Méthode de paiement: %s - %s' % (self.id, self.price, self.get_method_display(), s)

#------------------------------------------------------------------------------
GENDER_CHOICES = ((constants.MALE, 'Homme'),
                  (constants.FEMALE, 'Femme'))

TSHIRT_CHOICES= (('S', 'S'),
                 ('M', 'M'),
                 ('L', 'L'),
                 ('XL', 'XL'))

class People(models.Model):
    """
    List of people that will run for this event.
    """
    first_name = models.CharField('Prénom', max_length=30)
    last_name = models.CharField('Nom', max_length=30)
    gender = models.CharField('Sexe', max_length=1, choices=GENDER_CHOICES)
    birthday = models.DateField('Date de naissance')

    # additional informations (can be null and blank)
    # some items have a relation with other models.
    license_nb = models.CharField('Numéro de licence', max_length=30, blank=True, null=True)
    school = models.ForeignKey(School, verbose_name='Ecole', blank=True, null=True)
    federation = models.ForeignKey(Federation, verbose_name='Fédération', blank=True, null=True)
    company = models.ForeignKey(Company, verbose_name='Entreprise', blank=True, null=True)
    club = models.ForeignKey(Club, verbose_name='Club', blank=True, null=True)
    tshirt = models.CharField('Taille tshirt', max_length=4, choices=TSHIRT_CHOICES,
                              blank=True, null=True)

    # for the management
    certificat = models.BooleanField('Certificat médical', default=False)
    legal_status = models.BooleanField('Status légal', default=False)  # for minor
    num = models.PositiveIntegerField('Numéro de dossard', unique=True,
                                      help_text='Pour obtenir les derniers dossards, laisser vide')
    time = models.DurationField('Temps', blank=True, null=True)
    ready = models.BooleanField('Prêt à courir', default=False)

    def age(self, ffa=True):
        """
        :arg bool ffa:
            Calculate age according to FFA.

        :returns:
            If ffa=True, returns the number of year between year of birth and
            year of this season.
            Else, returns current age.
        """
        if not self.birthday:
            return None
        if ffa:
            num_years = datetime.date.today().year - self.birthday.year
        else:
            today = datetime.date.today()
            num_years = int((today - self.birthday).days / 365.2425)
        return num_years

    def runner_category(self):
        """
        Category are given by FFA
        """
        age = self.age(ffa=True)
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
        if age is not None and age < 14:
            return False
        else:
            return True

    def is_adult(self):
        """
        TODO
        """
        age = self.age()
        # TODO: can be manageable
        if age >= 18:
            return True
        else:
            return False

    def clean(self):
        """
        Check num
        Check if runner can run
        """
        err = []
        if not self.num:
            err = self.list_last_num()

        if not self.can_run():
            # raise an error and avoid registration
            err.append('%s ne peut pas s\'inscrire, l\'âge minimale est de '
                       '14 ans, ce dernier ayant %s ans.' % (self, self.age()))
        if err:
            raise ValidationError(
                {
                    NON_FIELD_ERRORS: err
                }
            )

    def list_last_num(self):
        num = []
        data = {
            'Individuel': RANGE_INDIVIDUAL,
            'Equipe - 1': RANGE_TEAM[0],
            'Equipe - 2': RANGE_TEAM[1],
            'Equipe - 3': RANGE_TEAM[2],
        }
        for name, r in data.iteritems():
            query = People.objects.filter(num__gte=r[0]).filter(num__lte=r[1]).order_by('-num')
            if query:
                num.append('%s - dernier dossard %s (interval %s)' % (name, query[0].num, r))
            else:
                num.append('%s - pas de dernier dossard (interval %s)' % (name, r))
        return num

    def update_num(self, r):
        query = People.objects.filter(num__gte=r[0]).filter(num__lte=r[1]).order_by('-num')
        if query:
            self.num = query[0].num + 1
            if self.num > r[1]:
                raise ValidationError('Oops, il semblerait qu\'il y ait trop d\'inscrits. Contactez un responsable.')
        else:
            self.num = r[0]

    class Meta:
        verbose_name = 'Personne'
        # unicity of People, avoid duplication
        unique_together = ('first_name', 'last_name', 'birthday', 'gender')

    def __str__(self):
        return '%s %s (%d)' % (self.first_name, self.last_name, self.num)

#------------------------------------------------------------------------------
class Runner(models.Model):
    """
    TODO
    """
    team = models.CharField('Nom de l\'équipe', max_length=30, blank=True, null=True)
    email = models.EmailField('Email')
    category = models.CharField('Catégorie du coureur', max_length=20, choices=CATEGORY_CHOICES,
                                default='Adulte')
    # OneToOne relation between People and Team
    runner_1 = models.OneToOneField(People, verbose_name='1er coureur',
                                    related_name='runner_1')
    runner_2 = models.OneToOneField(People, verbose_name='2nd coureur',
                                    related_name='runner_2', blank=True, null=True)
    runner_3 = models.OneToOneField(People, verbose_name='3eme coureur',
                                    related_name='runner_3', blank=True, null=True)
    company = models.ForeignKey(Company, verbose_name='Entreprise', blank=True, null=True)
    # OneToOne relation between Payment and Team
    payment = models.OneToOneField(Payment, verbose_name='Paiement')

    def delete(self, *args, **kwargs):
        """
        When deleting a Runner, delete all related objects.
        """
        self.runner_1.delete()
        if self.team:
            self.runner_2.delete()
            self.runner_3.delete()
        self.payment.delete()
        super(Runner, self).delete(*args, **kwargs)

    class Meta:
        verbose_name = 'Coureur'

    def __str__(self):
        if self.team:
            return 'Equipe: %s' % self.team
        else:
            return '%s %s' % (self.runner_1.first_name, self.runner_1.last_name)
