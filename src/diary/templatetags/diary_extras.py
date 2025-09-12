from django import template
register = template.Library()

@register.filter
def get_item(dct, key):
    return dct.get(key)