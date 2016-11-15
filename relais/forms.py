from captcha.fields import CaptchaField
from django import forms
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS

from relais import helpers, constants
from relais.constants import RANGE_INDIVIDUAL, RANGE_TEAM
from relais.models import (
    CATEGORY_CHOICES,
    CONFIG_CHOICES,
    METHOD_PAYMENT_CHOICES,
    GENDER_CHOICES,
    TSHIRT_CHOICES,
    Runner,
    Individual,
    Team,
)


#------------------------------------------------------------------------------
class RulesForm(forms.Form):
    """
    Validate rules at the beginning of the event.
    """
    checkbox = forms.BooleanField(label="check", widget=forms.CheckboxInput(),
                                  error_messages={'required': "Vous devez accepter " \
                                                              "la décharge et le règlement"})

#------------------------------------------------------------------------------
class ConfigForm(forms.Form):
    """
    Configuration choice (Individual vs Team)
    """
    choice = forms.ChoiceField(label='Choix', choices=CONFIG_CHOICES)

#------------------------------------------------------------------------------
class SubscriptionForm(forms.Form):
    required_css_class = 'required'

    email = forms.EmailField(label='Email')
    category = forms.ChoiceField(label='Catégorie', choices=CATEGORY_CHOICES)

    school = forms.CharField(label='Ecole', required=False)
    company = forms.CharField(label='Entreprise', required=False)
    club = forms.CharField(label='Club', required=False)

    canicross = forms.BooleanField(label='Canicross',
                                   help_text='Cochez cette case si vous courrez avec votre chien',
                                   required=False)


    def __init__(self, *args, **kwargs):
        self.is_a_team = kwargs.pop('is_a_team', False)
        self.onsite = kwargs.pop('onsite', True)

        super(SubscriptionForm, self).__init__(*args, **kwargs)

        if self.is_a_team:
            self.nb = 3
            self.fields['name'] = forms.CharField(label='Nom')
        else:
            self.nb = 1

        for i in range(self.nb):
            self.fields['first_name_%d' % i] = forms.CharField(label='Prénom',
                                                               max_length=30)
            self.fields['last_name_%d' % i] = forms.CharField(label='Nom',
                                                              max_length=30)
            self.fields['gender_%d' % i] = forms.ChoiceField(label='Sexe',
                                                             choices=GENDER_CHOICES)
            self.fields['birthday_%d' % i] = forms.DateField(label='Date de naissance')
            self.fields['license_%d' % i] = forms.CharField(label='Numéro de licence',
                                                            max_length=30, required=False)
            self.fields['federation_%d' % i] = forms.CharField(label='Fédération',
                                                               required=False)
            self.fields['club_%d' % i] = forms.CharField(label='Club',
                                                         required=False)
            self.fields['tshirt_%d' % i] = forms.ChoiceField(label='Taille t-shirt', choices=TSHIRT_CHOICES,
                                                             help_text='Les 150 premiers inscrits ont droit à un'
                                                             'tshirt technique offert',
                                                             required=False)
            if self.onsite:
                self.fields['num_%d' % i] = forms.IntegerField(label='Numéro de dossard')
        if not self.onsite:
            self.fields['captcha'] = CaptchaField()

    def clean(self):
        """
        Clean incoming data (after POST request for example) and check
        validation.
        """
        cleaned_data = super(SubscriptionForm, self).clean()  # call default method
        r = []
        # each Runner must be unique
        for i in range(self.nb):
            first_name = self.cleaned_data.get('first_name_%d' % i)
            last_name = self.cleaned_data.get('last_name_%d' % i)
            birthday = self.cleaned_data.get('birthday_%d' % i)
            gender = self.cleaned_data.get('gender_%d' % i)
            num = self.cleaned_data.get('num_%d' % i, None)
            if not None in (first_name, last_name, birthday, gender):
                r.append(Runner(first_name=first_name,
                              last_name=last_name,
                              birthday=birthday,
                              gender=gender,
                              num=num))
                if not num:
                    if self.is_a_team:
                        r[i].update_num(RANGE_TEAM[i])
                    else:
                        r[i].update_num(RANGE_INDIVIDUAL)
                self.cleaned_data['num_%d' % i]  = r[i].num
                r[i].clean()
                try:
                    r[i].validate_unique()
                except ValidationError as e:
                    if dict(e).get('num'):
                        raise ValidationError(
                        {
                            NON_FIELD_ERRORS: [
                                'Numéro de dossard %s déjà pris' % num
                            ],
                        }
                        )
                    raise ValidationError(
                        {
                            NON_FIELD_ERRORS: [
                                'Le coureur %s %s existe déjà' % (first_name, last_name)
                            ],
                        }
                    )
                # TODO: improve this (return Runner object ?)
                self.cleaned_data['legal_status_%d' % i] = r[i].is_adult()
            # convert name -> id (ForeignKey)
            self.cleaned_data['club_%d' % i] = helpers.add_get_club(self.cleaned_data.get('club_%d' % i))
            self.cleaned_data['federation_%d' % i] = helpers.add_get_fede(self.cleaned_data.get('federation_%d' % i))

        if self.is_a_team:
            # check if Team is unique
            t = Team(runner_1=r[0], runner_2=r[1], runner_3=r[2],
                     name=self.cleaned_data.get('name'),
                     email=self.cleaned_data.get('email'))
            t.clean()
            t.validate_unique()
        else:
            ind = Individual(runner=r[0])
            ind.clean()
            ind.validate_unique()

        # convert name -> id (ForeignKey)
        self.cleaned_data['school'] = helpers.add_get_school(self.cleaned_data.get('school'))
        self.cleaned_data['company'] = helpers.add_get_company(self.cleaned_data.get('company'))

        return cleaned_data

#------------------------------------------------------------------------------
class PaymentForm(forms.Form):
    # little bastard no ? :)
    # just remove unknown payment for user form
    choices = ((i, name) for i, name in METHOD_PAYMENT_CHOICES if i != constants.UNKNOWN)
    method = forms.ChoiceField(label='Méthode', choices=choices)
