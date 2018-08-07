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
from django.utils.translation import ugettext_lazy
from base.models.learning_unit_year import LearningUnitYear
from django.utils.translation import ugettext_lazy as _

FIELDS_FOR_LEARNING_UNIT_YR_COMPARISON = ['acronym', 'subtype', 'internship_subtype', 'credits', 'periodicity',
                                          'status', 'language', 'professional_integration', 'specific_title',
                                          'specific_title_english', 'quadrimester',
                                          'session', 'attribution_procedure']
FIELDS_FOR_LEARNING_CONTAINER_YR_COMPARISON = ['team', 'is_vacant', 'type_declaration_vacant']
DEFAULT_VALUE_FOR_NONE = '-'


def get_keys(list1, list2):
    keys = list1
    for k in list2:
        if k not in keys:
            keys.append(k)
    return sorted(keys, key=ugettext_lazy)


def compare_learning_unit_years(obj_ref, obj):
    return _compare(obj_ref, obj, FIELDS_FOR_LEARNING_UNIT_YR_COMPARISON)


def compare_learning_container_years(obj_ref, obj):
    return _compare(obj_ref, obj, FIELDS_FOR_LEARNING_CONTAINER_YR_COMPARISON)


def _compare(obj1, obj2, included_keys):
    data_obj1, data_obj2 = obj1.__dict__, obj2.__dict__
    return _get_changed_values(data_obj1, data_obj2, included_keys, type(obj1))


def _get_changed_values(data_obj1, data_obj2, included_keys, model):
    changed_values = {}
    for key, value in data_obj1.items():
        if key not in included_keys:
            continue
        try:
            if value != data_obj2[key]:
                changed_values.update({key: get_value(model, data_obj2, key)})
        except KeyError:
            raise KeyError('Invalid key for learning_unit_year compare')
    return changed_values


def get_value(model, data, field_name):
    value = data.get(field_name, DEFAULT_VALUE_FOR_NONE)
    if model._meta.get_field(field_name).choices:
        return _(value) if value else DEFAULT_VALUE_FOR_NONE
    elif model._meta.get_field(field_name).get_internal_type() == 'BooleanField':
        return _decrypt_boolean_value(field_name, value)
    else:
        return value


def _get_boolean_translation(value):
    return _('yes') if value else _('no')


def _get_status(value):
    return _('ACTIVE') if value else _('inactive')


def _decrypt_boolean_value(field_name, value):
    if field_name == 'status':
        return _get_status(value)
    else:
        return _get_boolean_translation(value)
