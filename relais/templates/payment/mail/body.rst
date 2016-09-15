Bonjour,

{% block content %}{% endblock %}

Pour toutes questions complémentaires liées à la course, visitez notre site
{{setting.url_home}} ou contactez par email l'équipe organisatrice à {{setting.email_contact}}

Pour tout problèmes ou questions liés à l'inscription, contactez {{setting.email}}

Rendez vous le {{setting.event|date('l d F') }} pour le Relais de l'ENSIL !

Sportivement vôtre,

---
L'Equipe du Relais de l'ENSIL
Site: {{setting.url_home}}
Adresse: {{setting.postal_address}}
Téléphone: {{setting.phone}}
Contact course: {{setting.email_contact}}
Contact inscription: {{setting.email}}
