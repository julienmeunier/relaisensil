from django.conf.urls import url

from relais.views import registration


urlpatterns = [
    url(r'^$', registration.index),
    url(r'^category/$', registration.category),
    url(r'^category/individual/$', registration.individual),
    url(r'^category/team/$', registration.team),
]
