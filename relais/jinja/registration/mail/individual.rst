{% extends "registration/mail/body.rst" %}
{% from "registration/mail/macros.rst" import display_runner %}
{% block content %}
=================================================================
Coureur 10 km - route (3,3 km) / nature (3,4 km) / route (3,3 km)
=================================================================
Catégorie
---------
{{category[r.category]}}

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

{%- endif -%}

Information sur le coureur
--------------------------
{{ display_runner(r.runner_1) }}
{% endblock %}