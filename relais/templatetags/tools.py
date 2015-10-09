from django import template
from relais import constants


register = template.Library()

def key(d, key_name):
    return d.get(key_name, 'N/A')

key = register.filter('key', key)

@register.simple_tag
def adult():
    return constants.ADULT

@register.simple_tag
def student():
    return constants.STUDENT

@register.simple_tag
def challenge():
    return constants.CHALLENGE

@register.simple_tag
def ensil():
    return constants.STUDENT_ENSIL

@register.simple_tag
def old_ensil():
    return constants.OLDER_ENSIL

@register.filter(name='addcss')
def addcss(field, css):
    return field.as_widget(attrs={"class": css})
