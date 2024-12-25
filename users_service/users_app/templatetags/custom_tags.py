from django import template

register = template.Library()


@register.simple_tag
def all_posts_url():
    return f'/api/pst/'


@register.simple_tag
def create_post_url():
    return f'/api/pst/post/'


@register.simple_tag
def posts_by_author_url(author_id):
    return f'/api/pst/find_by_author/?author_id={author_id}'


@register.simple_tag
def your_chat_url():
    return f'/chat/'
