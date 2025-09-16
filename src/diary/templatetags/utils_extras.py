# src/diary/templatetags/utils_extras.py
from django import template

register = template.Library()

@register.filter
def get_item(d, key):
    """
    Безопасно возвращает d[key] для словаря d (или None).
    Использование в шаблоне: {{ mydict|get_item:mykey }}
    """
    try:
        return d.get(key)
    except Exception:
        return None