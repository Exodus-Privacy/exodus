from django import template
from django.template.defaultfilters import stringfilter

import mistune

register = template.Library()


@register.filter(name='markdown', is_safe=True)
@stringfilter
def markdown(value):
    m = mistune.Markdown()
    return m(value)
