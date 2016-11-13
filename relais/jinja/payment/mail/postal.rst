{% extends 'payment/mail/body.rst' %}
{% block content %}
Vous avez choisi un paiement en liquide / chèque pour l'inscription du
Relais de l'ENSIL ({{name}})

Vous pouvez nous l'envoyer par voie postale à {{setting.postal_address}} en
précisant les numéros suivants, avant le {{setting.closure_online|date('l d F')}}

- ID: {{payment.id}}
- Token: {{payment.token}}
- Montant: {{payment.price.price}} €

Information actuelle sur le paiement: {{payment}}
{% endblock %}
