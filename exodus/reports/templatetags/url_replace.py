from django import template

register = template.Library()


@register.simple_tag
def url_replace(request, field, value):
    """
    Utility function to replace the value of a specified parameter in URL
    """
    get_dict = request.GET.copy()
    get_dict[field] = value
    return get_dict.urlencode()
