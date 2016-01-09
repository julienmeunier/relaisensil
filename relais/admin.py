from django.contrib import admin
from relais.models import (
    Club,
    Company,
    Federation,
    Payment,
    Individual,
    Team,
    Runner,
    School,
    Price,
    Setting,
)

#------------------------------------------------------------------------------
class SettingAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        # if there's already an entry, do not allow adding
        count = Setting.objects.all().count()
        if count == 0:
            return True
        return False

admin.site.register(Setting, SettingAdmin)

#------------------------------------------------------------------------------
class PriceAdmin(admin.ModelAdmin):
    list_display = ['when', 'who', 'config', 'price']

admin.site.register(Price, PriceAdmin)

#------------------------------------------------------------------------------
class IndividualAdmin(admin.ModelAdmin):
    list_display = ('id', 'runner_link', 'runner_certificat', 'payment_link', 'payment_status')
    actions = ['really_delete_selected']

    # by default, django use QuerySet to delete an entry
    # however, in the case of Individual/Team, delete method of these models
    # must be called in order to clean up other models
    def get_actions(self, request):
        actions = super(IndividualAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def really_delete_selected(self, request, queryset):
        for obj in queryset:
            obj.delete()

        self.message_user(request, u"%s coureur(s) correctement supprime(s)." % queryset.count())
    really_delete_selected.short_description = u"Supprimer un coureur (+ paiement)"

    # add a link to the Runner admin page
    def runner_link(self, obj):
        return '<a href="/admin/relais/runner/%s">%s</a>' % (obj.runner.pk, obj.runner)
    runner_link.allow_tags = True

    def payment_link(self, obj):
        return '<a href="/admin/relais/payment/%s">Access to payment</a>' % obj.payment.pk
    payment_link.allow_tags = True

    # display items for another models in the admin page
    def runner_certificat(self, obj):
        return obj.runner.certificat
    runner_certificat.boolean = True
    runner_certificat.short_description = 'Certificat'

    def payment_status(self, obj):
        return obj.payment.state
    payment_status.boolean = True
    payment_status.short_description = 'Payment'

admin.site.register(Individual, IndividualAdmin)

#------------------------------------------------------------------------------
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'token', 'reverse', 'method', 'price', 'state', 'ipn_link')

    def reverse(self, obj):
        try:
            return '<a href="/admin/relais/individual/%s">%s</a>' % (obj.individual.pk,
                                                                     obj.individual)
        except Individual.DoesNotExist:
            return '<a href="/admin/relais/team/%s">%s</a>' % (obj.team.pk, obj.team)
    reverse.short_description = 'Origine'
    reverse.allow_tags = True

    # display paypal link in admin page if available
    def ipn_link(self, obj):
        if obj.ipn:
            return '<a href="/admin/ipn/paypalipn/%s">Access to PayPal</a>' % obj.ipn.pk
        else:
            return 'N/A'
    ipn_link.allow_tags = True

admin.site.register(Payment, PaymentAdmin)

#------------------------------------------------------------------------------
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name',
                    'runner_1_link',
                    'runner_1_certificat',
                    'runner_2_link',
                    'runner_2_certificat',
                    'runner_3_link',
                    'runner_3_certificat',
                    'company',
                    'payment')
    actions = ['really_delete_selected']

    # by default, django use QuerySet to delete an entry
    # however, in the case of Individual/Team, delete method of these models
    # must be called in order to clean up other models
    def get_actions(self, request):
        actions = super(TeamAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def really_delete_selected(self, request, queryset):
        for obj in queryset:
            obj.delete()

        self.message_user(request, u"%s equipe(s) correctement supprime(s)." % queryset.count())
    really_delete_selected.short_description = u"Supprimer une equipe (+ paiement + coureurs)"

    # add a link to the Runner admin page
    def runner_1_link(self, obj):
        return '<a href="/admin/relais/runner/%s">%s</a>' % (obj.runner_1.pk, obj.runner_1)
    runner_1_link.allow_tags = True

    # add a link to the Runner admin page
    def runner_2_link(self, obj):
        return '<a href="/admin/relais/runner/%s">%s</a>' % (obj.runner_2.pk, obj.runner_2)
    runner_2_link.allow_tags = True

    # add a link to the Runner admin page
    def runner_3_link(self, obj):
        return '<a href="/admin/relais/runner/%s">%s</a>' % (obj.runner_3.pk, obj.runner_3)
    runner_3_link.allow_tags = True

    def payment_link(self, obj):
        return '<a href="/admin/relais/payment/%s">Access to payment</a>' % obj.payment.pk
    payment_link.allow_tags = True

    # display items for another models in the admin page
    def runner_1_certificat(self, obj):
        return obj.runner_1.certificat
    runner_1_certificat.boolean = True
    runner_1_certificat.short_description = 'Cert. 1'

    # display items for another models in the admin page
    def runner_2_certificat(self, obj):
        return obj.runner_2.certificat
    runner_2_certificat.boolean = True
    runner_2_certificat.short_description = 'Cert. 2'

    # display items for another models in the admin page
    def runner_3_certificat(self, obj):
        return obj.runner_3.certificat
    runner_3_certificat.boolean = True
    runner_3_certificat.short_description = 'Cert. 3'

    def payment_status(self, obj):
        return obj.payment.state
    payment_status.boolean = True
    payment_status.short_description = 'Payment'
admin.site.register(Team, TeamAdmin)

#------------------------------------------------------------------------------
class RunnerAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'first_name', 'certificat', 'legal_status', 'num', 'canicross', 'tshirt']

admin.site.register(Runner, RunnerAdmin)

#------------------------------------------------------------------------------
# Classic admin for other models
admin.site.register(Club)
admin.site.register(Company)
admin.site.register(Federation)
admin.site.register(School)
