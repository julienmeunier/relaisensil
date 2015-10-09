from django.conf.urls import url

from relais.views import payment


urlpatterns = [
    url(r'^(?P<idpay>\d+)/(?P<token>\w+)$', payment.update_method),
]
