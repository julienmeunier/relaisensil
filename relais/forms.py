#-*-coding: utf-8 -*-
from captcha.fields import CaptchaField
from django import forms
from django.utils.translation import ugettext as _

from relais import helpers, constants
from relais.models import (
    CATEGORY_CHOICES,
    CONFIG_CHOICES,
    METHOD_PAYMENT_CHOICES,
    GENDER_CHOICES,
    Runner,
    Individual,
    Team
)
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS


#------------------------------------------------------------------------------
class RulesForm(forms.Form):
    """
    Validate rules at the beginning of the event.
    """
    checkbox = forms.BooleanField(label="check", widget=forms.CheckboxInput())

#------------------------------------------------------------------------------
class ConfigForm(forms.Form):
    """
    Configuration choice (Individual vs Team)
    """
    choice = forms.ChoiceField(label=_("Choice"), choices=CONFIG_CHOICES)

#------------------------------------------------------------------------------
class IndividualForm(forms.Form):
    """
    Individual form: mix of Runner and Individual models.
    """
    first_name = forms.CharField(label=_("First Name"), max_length=30)
    last_name = forms.CharField(label=_("Last Name"), max_length=30)
    email = forms.EmailField(label=_("Email"))
    gender = forms.ChoiceField(label=_('Gender'), choices=GENDER_CHOICES)
    birthday = forms.DateField(label=_('Birthday'))
    category = forms.ChoiceField(label=_('Category'), choices=CATEGORY_CHOICES)

    license = forms.CharField(label=_('License number'), max_length=30, required=False)
    school = forms.CharField(label=_('School'), required=False)
    federation = forms.CharField(label=_('Federation'), required=False)
    company = forms.CharField(label=_('Company'), required=False)
    club = forms.CharField(label=_('Club'), required=False)

    captcha = CaptchaField()

    def clean(self):
        """
        Clean incoming data (after POST request for example) and check
        validation.
        """
        cleaned_data = super(IndividualForm, self).clean()  # call default method

        # use Runner model checking methods
        first_name = self.cleaned_data.get('first_name')
        last_name = self.cleaned_data.get('last_name')
        birthday = self.cleaned_data.get('birthday')
        gender = self.cleaned_data.get('gender')
        if not None in (first_name, last_name, birthday, gender):
            runner = Runner(first_name=first_name,
                            last_name=last_name,
                            birthday=birthday,
                            gender=gender)
            runner.clean()
            runner.validate_unique()
            # TODO: improve this (return Runner object ?)
            self.cleaned_data['num'] = runner.num
            self.cleaned_data['legal_status'] = runner.is_minor()
            ind = Individual(runner=runner)
            ind.clean()
            ind.validate_unique()

        # convert name -> id for ForeignKey
        self.cleaned_data['club'] = helpers.add_get_club(self.cleaned_data.get('club'))
        self.cleaned_data['school'] = helpers.add_get_school(self.cleaned_data.get('school'))
        self.cleaned_data['company'] = helpers.add_get_company(self.cleaned_data.get('company'))
        self.cleaned_data['federation'] = helpers.add_get_fede(self.cleaned_data.get('federation'))

        return cleaned_data

#------------------------------------------------------------------------------
class TeamForm(forms.Form):
    """
    Individual form: mix of Runners and Team models.
    """
    required_css_class = 'required'
    name = forms.CharField(label=_("Name"))
    email = forms.EmailField(label=_("Email"))
    category = forms.ChoiceField(label=_('Category'), choices=CATEGORY_CHOICES)

    company = forms.CharField(label=_('Company'), required=False,
                              help_text=_('Complete it if you run with your company'))
    school = forms.CharField(label=_('School'), required=False)

    captcha = CaptchaField()

    # redefine constructor
    def __init__(self, *args, **kwargs):
        super(TeamForm, self).__init__(*args, **kwargs)
        # as there are 3 runners for a Team, to avoid code duplication,
        # let's use a loop
        for i in xrange(1, 4):
            self.fields['first_name_%d' % i] = forms.CharField(label=_("First Name"),
                                                               max_length=30)
            self.fields['last_name_%d' % i] = forms.CharField(label=_("Last Name"),
                                                              max_length=30)
            self.fields['gender_%d' % i] = forms.ChoiceField(label=_('Gender'),
                                                             choices=GENDER_CHOICES)
            self.fields['birthday_%d' % i] = forms.DateField(label=_('Birthday'))
            self.fields['license_%d' % i] = forms.CharField(label=_('License number'),
                                                            max_length=30, required=False)
            self.fields['federation_%d' % i] = forms.CharField(label=_('Federation'),
                                                               required=False)
            self.fields['club_%d' % i] = forms.CharField(label=_('Club'),
                                                         required=False)

    def clean(self):
        """
        Clean incoming data (after POST request for example) and check
        validation.
        """
        cleaned_data = super(TeamForm, self).clean()  # call default method
        r = {}
        # each Runner must be unique
        for i in xrange(1, 4):
            first_name = self.cleaned_data.get('first_name_%d' % i)
            last_name = self.cleaned_data.get('last_name_%d' % i)
            birthday = self.cleaned_data.get('birthday_%d' % i)
            gender = self.cleaned_data.get('gender_%d' % i)
            if not None in (first_name, last_name, birthday, gender):
                r[i] = Runner(first_name=first_name,
                              last_name=last_name,
                              birthday=birthday,
                              gender=gender)
                r[i].clean()
                try:
                    r[i].validate_unique()
                except ValidationError:
                    raise ValidationError(
                        {
                            NON_FIELD_ERRORS: [
                                u'Le coureur %d existe déjà' % i
                            ],
                        }
                    )
                # TODO: improve this (return Runner object ?)
                self.cleaned_data['legal_status_%d' % i] = r[i].is_minor()
            # convert name -> id (ForeignKey)
            self.cleaned_data['club_%d' % i] = helpers.add_get_club(self.cleaned_data.get('club_%d' % i))
            self.cleaned_data['federation_%d' % i] = helpers.add_get_fede(self.cleaned_data.get('federation_%d' % i))

        # check if Team is unique
        t = Team(runner_1=r[1], runner_2=r[2], runner_3=r[3],
                 name=self.cleaned_data.get('name'),
                 email=self.cleaned_data.get('email'))
        t.clean()
        t.validate_unique()

        # convert name -> id (ForeignKey)
        self.cleaned_data['school'] = helpers.add_get_school(self.cleaned_data.get('school'))
        self.cleaned_data['company'] = helpers.add_get_company(self.cleaned_data.get('company'))

        return cleaned_data

#------------------------------------------------------------------------------
class PaymentForm(forms.Form):
    # little bastard no ? :)
    # just remove unknown payment for user form
    choices = ((i, name) for i, name in METHOD_PAYMENT_CHOICES if i != constants.UNKNOWN)
    method = forms.ChoiceField(label=_('Method'), choices=choices)
