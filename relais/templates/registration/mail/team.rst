{% extends "registration/mail/body.rst" %}
{% load macros %}
{% load tools %}
{% loadmacros "registration/mail/macros.rst" %}
{% block content %}
=====================
Equipe de 3 personnes
=====================
Catégorie
---------
{{category|[team.category}}}

Nom de l'équipe
---------------
{{team.name}}

Prix
----
{{team.payment.price.price}} €

{% if team.company %}
Entreprise
----------
{{team.company}}
{% endif %}

{% if team.school %}
Ecole
-----
{{team.school}}
{% endif %}

Information sur les coureurs
----------------------------

Coureur 1: route (3,3 km)
~~~~~~~~~~~~~~~~~~~~~~~~~~
{{ display_runner(team.runner_1) }}

Coureur 2: nature (3,4 km)
~~~~~~~~~~~~~~~~~~~~~~~~~~
{{ display_runner(team.runner_2) }}

Coureur 3: route (3,3 km)
~~~~~~~~~~~~~~~~~~~~~~~~~~
{{ display_runner(team.runner_3) }}
{% endblock %}