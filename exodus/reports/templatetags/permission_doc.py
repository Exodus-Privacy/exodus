from django import template
from django.template.defaultfilters import stringfilter
from django.db.models.query import QuerySet

register = template.Library()


@register.filter(name='perm_doc', is_safe=True)
def perm_doc(value):
    perm = str(value)
    if perm.startswith('android.permission.'):
        perm = perm.replace('android.permission.', '')
        return '<a href="https://developer.android.com/reference/android/Manifest.permission.html#%s" target="_blank">ℹ️</a>'

    return ''