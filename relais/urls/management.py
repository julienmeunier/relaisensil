from django.conf.urls import url

from relais.views import management


urlpatterns = [
    url(r'^$', management.index),
    url(r'^listing$', management.listing),
    url(r'^results/individual', management.results_individual),
    url(r'^results/team', management.results_team),
    url(r'^results', management.results),
    url(r'^fictive$', management.create_fake_users),
    url(r'^status$', management.status),

]
