from django import template
register = template.Library()

@register.simple_tag(takes_context=True)
def is_moderator(context):
    user = context["request"].user
    if not user.is_authenticated:
        return False
    return user.is_staff or user.groups.filter(name="moderators").exists()