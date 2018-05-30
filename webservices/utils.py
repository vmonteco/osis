from django.http import Http404


def to_int_or_404(year):
    try:
        return int(year)
    except:
        raise Http404


def convert_sections_to_list_of_dict(sections):
    return [{
        'id': key,
        'label': value['label'],
        'content': value['content']
    } for key, value in sections.items()]


def convert_sections_list_of_dict_to_dict(sections):
    return {
        item['id']: {
            'label': item['label'],
            'content': item['content']
        }
        for item in sections
    }

