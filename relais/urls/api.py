from django.conf.urls import url

from relais.views import api


urlpatterns = [
    url(r'^runner/get$', api.get_runner),
    url(r'^time/set_go$', api.set_top_time_dynamic),
    url(r'^time/set$', api.set_time),
    url(r'^time/set_auto$', api.set_dynamic_time),
]
