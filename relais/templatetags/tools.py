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

'''
usage
{% ++ <var_name> %}
For example
{% ++ a %}
'''

def increment_var(parser, token):

    parts = token.split_contents()
    if len(parts) < 2:
        raise template.TemplateSyntaxError("'increment' tag must be of the form:  {% increment <var_name> %}")
    return IncrementVarNode(parts[1])

register.tag('++', increment_var)

class IncrementVarNode(template.Node):

    def __init__(self, var_name):
        self.var_name = var_name

    def render(self,context):
        try:
            value = context[self.var_name]
            context[self.var_name] = value + 1
            return u""
        except:
            raise template.TemplateSyntaxError("The variable does not exist.")