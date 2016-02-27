from django.conf.urls import url

from relais.views import management, registration_offline


urlpatterns = [
    url(r'^$', management.index),
    url(r'^listing$', management.listing),
    url(r'^listing/individual$', management.results_individual, {'display_all': True, 'order_by_time': False }),
    url(r'^listing/team$', management.results_team, {'display_all': True, 'order_by_time': False }),
    url(r'^timing$', management.timing),
    url(r'^timing_auto$', management.timing_auto),
    url(r'^results/individual(/all)?$', management.results_individual),
    url(r'^results/team(/all)?$', management.results_team),
    url(r'^results$', management.results),
    url(r'^registration$', registration_offline.index),
    url(r'^registration/category/$', registration_offline.category),
    url(r'^registration/category/individual/$', registration_offline.individual),
    url(r'^registration/category/team/$', registration_offline.team),
    url(r'^registration/end/([\w]+)/([0-9]+)$', registration_offline.end),
#     url(r'^fictive$', management.create_fake_users),
]
