{% macro display_runner(runner) %}
Nom: {{runner.last_name}}
Prénom: {{runner.first_name}}
Date de naissance: {{runner.birthday}}

{%- if runner.federation -%}
Fédération: {{runner.federation}}
{%- endif -%}
{%- if runner.license_num -%}
Numéro de licence: {{runner.license_numl}}
{%- endif -%}
{%- if runner.is_minor -%}
La personne étant mineure, la décharge de responsabilité ({{ static('pdf/autorisation.pdf')}})
doit nous être renvoyée par courriel ou par voie postale.
{%- endif -%}
{% endmacro %}