import logging

from django import template

logger = logging.getLogger('logger')

register = template.Library()


@register.filter(name='get_item')
def get_item(dictionary, key):
    logger.debug(f'get_item: dictionary: {dictionary}, key: {key}')
    logger.debug(f'get_item: Type dictionary: {type(dictionary)}')
    if dictionary is not None:
        value = dictionary.get(str(key))
        logger.debug(f'get_item: value: {value}')
        return value
    return None
