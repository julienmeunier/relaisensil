{% extends 'payment/mail/body.rst' %}
{% block content %}
Votre paiement pour l'inscription du Relais de l'ENSIL ({{name}}) a été validé.

Rappel
======
ID: {{payment.id}}
Paiement: {{payment}}
{% endblock %}