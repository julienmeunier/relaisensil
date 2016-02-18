from django.conf.urls import url

from relais.views import management


urlpatterns = [
    url(r'^$', management.index),
    url(r'^listing$', management.listing),
    url(r'^listing/individual$', management.results_individual, {'display_all': True, 'order_by_time': False }),
    url(r'^listing/team$', management.results_team, {'display_all': True, 'order_by_time': False }),
    url(r'^timing$', management.timing),
    url(r'^results/individual(/all)?$', management.results_individual),
    url(r'^results/team(/all)?$', management.results_team),
    url(r'^results$', management.results),
    url(r'^fictive$', management.create_fake_users),
]
