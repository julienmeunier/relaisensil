{% extends "registration/mail/body.rst" %}
{% from "registration/mail/macros.rst" import display_runner %}
{% block content %}
=================================================================
Coureur 10 km - route (3,3 km) / nature (3,4 km) / route (3,3 km)
=================================================================
Catégorie
---------
{{category[individual.category]}}

Prix
----
{{individual.payment.price.price}} €

{%- if individual.company -%}

Entreprise
----------
{{individual.company}}

{% endif %}
{%- if individual.school -%}

Ecole
-----
{{individual.school}}

{%- endif -%}

Information sur le coureur
--------------------------
{{ display_runner(individual.runner) }}
{% endblock %}