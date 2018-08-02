##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2018 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django.utils.translation import ugettext_lazy as _


def get_value(model, data, field_name):
    if model._meta.get_field(field_name).choices:
        return translate(data[field_name])
    else:
        if model._meta.get_field(field_name).get_internal_type() == 'BooleanField':
            return _('yes') if data[field_name] else _('no')
        else:
            return data.get(field_name, None)


def translate(value):
    if value:
        return _(value)
    return None


def get_keys(list1, list2):
    keys = list1
    for k in list2:
        if k not in keys:
            keys.append(k)
    return get_list_sorted_by_translation(keys)


def get_list_sorted_by_translation(list_of_keys):
    return sorted(list_of_keys, key=get_translation)


def get_translation(item):
    return _(item)


