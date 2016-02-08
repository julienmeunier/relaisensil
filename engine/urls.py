from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin

from engine.settings import production
from relais.views import registration


admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', registration.index),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^registration/', include('relais.urls.registration')),
    url(r'^payment/', include('relais.urls.payment')),
    url(r'^paypal/', include('paypal.standard.ipn.urls')),
    url(r'^captcha/', include('captcha.urls')),
) + static(production.STATIC_URL, document_root=production.STATIC_ROOT)
