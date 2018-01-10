{% extends "registration/mail/body.rst" %}
{% from "registration/mail/macros.rst" import display_runner %}

{% block content %}
=====================
Equipe de 3 personnes
=====================
Catégorie
---------
{{category[r.category]}}

Nom de l'équipe
---------------
{{r.team}}

Prix
----
{{r.payment.price.price}} €

{%- if r.company -%}

Entreprise
----------
{{r.company}}

{% endif %}
{%- if r.school -%}

Ecole
-----
{{r.school}}

{% endif %}

Information sur les coureurs
----------------------------

Coureur 1: route (3,3 km)
~~~~~~~~~~~~~~~~~~~~~~~~~
{{ display_runner(r.runner_1) }}

Coureur 2: nature (3,4 km)
~~~~~~~~~~~~~~~~~~~~~~~~~~
{{ display_runner(r.runner_2) }}

Coureur 3: route (3,3 km)
~~~~~~~~~~~~~~~~~~~~~~~~~
{{ display_runner(r.runner_3) }}
{% endblock %}