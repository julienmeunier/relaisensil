from django.conf.urls import url

from relais.views import api


urlpatterns = [
    url(r'^runner/get$', api.get_runner),
    url(r'^time/set$', api.set_time),
]
