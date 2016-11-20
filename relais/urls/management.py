from django.conf.urls import url

from relais.views import management, registration


urlpatterns = [
    url(r'^$', management.index),
    url(r'^listing$', management.listing),
    url(r'^listing/individual$', management.results_individual, {'display_all': True, 'order_by_time': False }),
    url(r'^listing/team$', management.results_team, {'display_all': True, 'order_by_time': False }),
    url(r'^timing$', management.timing),
    url(r'^timing_auto$', management.timing_auto),
    url(r'^start_race$', management.start_race),
    url(r'^results/individual(/all)?$', management.results_individual),
    url(r'^results/team(/all)?$', management.results_team),
    url(r'^results$', management.results),
    url(r'^registration/$', registration.onsite, {'func': registration.index}),
    url(r'^registration/category/$', registration.onsite, {'func': registration.category}),
    url(r'^registration/category/individual/$', registration.onsite, {'func': registration.form, 'team': False}),
    url(r'^registration/category/team/$', registration.onsite, {'func': registration.form, 'team': True}),
    url(r'^registration/end/([\w]+)/([0-9]+)$', registration.onsite, {'func': registration.end}),
#     url(r'^fictive$', management.create_fake_users),
]
