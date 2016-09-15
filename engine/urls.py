from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin

from engine.settings import production
from relais.views import registration


admin.autodiscover()

urlpatterns = [
    url(r'^$', registration.index),
    url(r'^admin/', admin.site.urls),
    url(r'^registration/', include('relais.urls.registration')),
    url(r'^payment/', include('relais.urls.payment')),
    url(r'^management/', include('relais.urls.management')),
    url(r'^api/', include('relais.urls.api')),
    url(r'^paypal/', include('paypal.standard.ipn.urls')),
    url(r'^captcha/', include('captcha.urls')),
] + static(production.STATIC_URL, document_root=production.STATIC_ROOT)
