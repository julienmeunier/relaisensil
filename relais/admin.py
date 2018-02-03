from django.contrib import admin

from relais.models import (
    Club,
    Company,
    Federation,
    Payment,
    People,
    Price,
    Runner,
    School,
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
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'token', 'reverse', 'method', 'price', 'state', 'ipn_link')
    list_max_show_all = 500
    list_per_page = 500

    def make_valid(self, _, queryset):
        queryset.update(state=True)
    make_valid.short_description = "Valider le paiement"

    actions = [make_valid]

    def reverse(self, obj):
        return '<a href="/admin/relais/runner/%s">%s</a>' % (obj.runner.pk,
                                                             obj.runner)
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
class RunnerAdmin(admin.ModelAdmin):
    list_display = ('type',
                    'team',
                    'runner_1_link',
                    'runner_1_certificat',
                    'runner_2_link',
                    'runner_2_certificat',
                    'runner_3_link',
                    'runner_3_certificat',
                    'company',
                    'payment_status',
                    'payment_link')
    list_max_show_all = 500
    list_per_page = 500
    actions = [really_delete_selected, make_valid_cert, make_valid_payment]

    def type(self, obj):
        if obj.team:
            return 'Equipe'
        else:
            return 'Individuel'
    type.short_description = 'Type de course'
    type.allow_tags = True

    def make_valid_cert(self, request, queryset):
        for obj in queryset:
            obj.runner_1.certificat = True
            obj.runner_1.save()
            if obj.runner_2:
                obj.runner_2.certificat = True
                obj.runner_2.save()
            if obj.runner_3:
                obj.runner_3.certificat = True
                obj.runner_3.save()
    make_valid_cert.short_description = "Valider les certificats"

    def make_valid_payment(self, request, queryset):
        for obj in queryset:
            obj.payment.state = True
            obj.payment.save()
    make_valid_payment.short_description = "Valider le paiement"

    # by default, django use QuerySet to delete an entry
    # however, in the case of Individual/Team, delete method of these models
    # must be called in order to clean up other models
    def get_actions(self, request):
        actions = super(RunnerAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def really_delete_selected(self, request, queryset):
        for obj in queryset:
            obj.delete()
        self.message_user(request, "%s coureurs(s) correctement supprime(s)." % queryset.count())
    really_delete_selected.short_description = "Supprimer ? (+ paiement + coureurs)"

    # add a link to the People admin page
    def runner_1_link(self, obj):
        return '<a href="/admin/relais/people/%s">%s</a>' % (obj.runner_1.pk, obj.runner_1)
    runner_1_link.allow_tags = True

    # add a link to the People admin page
    def runner_2_link(self, obj):
        if obj.runner_2:
            return '<a href="/admin/relais/people/%s">%s</a>' % (obj.runner_2.pk, obj.runner_2)
        else:
            return None
    runner_2_link.allow_tags = True

    # add a link to the People admin page
    def runner_3_link(self, obj):
        if obj.runner_2:
            return '<a href="/admin/relais/people/%s">%s</a>' % (obj.runner_3.pk, obj.runner_3)
        else:
            return None
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
        if obj.runner_2:
            return obj.runner_2.certificat
        else:
            return None
    runner_2_certificat.boolean = True
    runner_2_certificat.short_description = 'Cert. 2'

    # display items for another models in the admin page
    def runner_3_certificat(self, obj):
        if obj.runner_3:
            return obj.runner_3.certificat
        else:
            return None
    runner_3_certificat.boolean = True
    runner_3_certificat.short_description = 'Cert. 3'

    def payment_status(self, obj):
        return obj.payment.state
    payment_status.boolean = True
    payment_status.short_description = 'Payment'
admin.site.register(Runner, RunnerAdmin)

#------------------------------------------------------------------------------
class PeopleAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'first_name', 'certificat', 'legal_status', 'num', 'tshirt', 'ready']
    list_max_show_all = 500
    list_per_page = 500

admin.site.register(People, PeopleAdmin)

#------------------------------------------------------------------------------
# Classic admin for other models
admin.site.register(Club)
admin.site.register(Company)
admin.site.register(Federation)
admin.site.register(School)
