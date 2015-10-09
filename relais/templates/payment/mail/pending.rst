{% extends 'payment/mail/body.rst' %}
{% block content %}
Votre paiement pour l'inscription du Relais de l'ENSIL ({{name}}) est en attente.

Rappel
======
ID: {{payment.id}}
Paiement: {{payment}}

Vous pouvez accéder à la page {{setting.url}}/payment/{{payment.id}}/{{payment.token}}
pour faire le choix de votre réglement.
{% endblock %}