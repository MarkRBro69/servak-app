from django import template

register = template.Library()


@register.simple_tag
def user_profile_url(author_id):
    return f'/api/usr/profile/{author_id}/'


@register.simple_tag
def user_desktop_url():
    return f'/api/usr/desktop/'
