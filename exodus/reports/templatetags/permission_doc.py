from django import template
from django.template.defaultfilters import stringfilter
from django.db.models.query import QuerySet

register = template.Library()


@register.filter(name='perm_doc', is_safe=True)
def perm_doc(value):
    perm = str(value)
    if perm.startswith('android.permission.') or \
            perm.startswith('com.google.android.c2dm.permission.') or \
            perm.startswith('com.google.android.gms.permission.') or \
            perm.startswith('com.google.android.googleapps.permission.'):
        return '<a class="" href="http://androidpermissions.com/permission/%s" target="_blank">Info️</a>' % perm

    return ''
