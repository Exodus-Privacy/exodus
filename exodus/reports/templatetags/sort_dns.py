from django import template
from django.db.models.query import QuerySet

register = template.Library()


@register.filter(name='sort_dns', is_safe=True)
def sort_dns(value):
    ret = []
    if isinstance(value, QuerySet):
        domains = {'.'.join(q.hostname.split('.')[-2:]) for q in value}
        # domains = {}
        # for q in value:
        #     domains |= ('.'.join(q.hostname.split('.')[-2:]))
        sorted_domains = []
        sorted_domains = list(domains)
        sorted_domains.sort()
        print(sorted_domains)
        for d in sorted_domains:
            tmp = []
            for q in value:
                if d in q.hostname:
                    tmp.append(q)
            # tmp.sort(key=lambda item: (len(item.hostname), item))
            ret += tmp
        return ret
    return value
