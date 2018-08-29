from django.template.defaulttags import register

@register.filter
def get_item(dictionnary, key):
    return dictionnary.get(key)