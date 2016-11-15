from django.conf.urls import url

from relais.views import registration


urlpatterns = [
    url(r'^$', registration.online, {'func': registration.index}),
    url(r'^category/$', registration.online, {'func': registration.category}),
    url(r'^category/individual/$', registration.online, {'func': registration.form, 'team': False}),
    url(r'^category/team/$', registration.online, {'func': registration.form, 'team': True}),
]
