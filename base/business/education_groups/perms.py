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
from django.core.exceptions import PermissionDenied
from django.utils.translation import ugettext_lazy as _, pgettext

from base.models import academic_calendar, group_element_year
from base.models.education_group_type import find_authorized_types
from base.models.enums import academic_calendar_type
from base.models.enums.education_group_categories import TRAINING, MINI_TRAINING, GROUP

ERRORS_MSG = {
    "base.add_educationgroup": "The user has not permission to create education groups.",
    "base.change_educationgroup": "The user has not permission to change education groups.",
    "base.delete_educationgroup": "The user has not permission to delete education groups.",
}


def is_eligible_to_add_training(person, education_group, raise_exception=False):
    return _is_eligible_to_add_education_group(person, education_group, TRAINING, raise_exception)


def is_eligible_to_add_mini_training(person, education_group, raise_exception=False):
    return _is_eligible_to_add_education_group(person, education_group, MINI_TRAINING, raise_exception)


def is_eligible_to_add_group(person, education_group, raise_exception=False):
    return _is_eligible_to_add_education_group(person, education_group, GROUP, raise_exception)


def _is_eligible_to_add_education_group(person, education_group, category, raise_exception=False):
    return check_permission(person, "base.add_educationgroup", raise_exception) and \
           _is_eligible_education_group(person, education_group, raise_exception) and \
           check_authorized_type(education_group, category, raise_exception)


def is_eligible_to_change_education_group(person, education_group, raise_exception=False):
    return check_permission(person, "base.change_educationgroup", raise_exception) and \
           _is_eligible_education_group(person, education_group, raise_exception)


def is_eligible_to_delete_education_group(person, education_group, raise_exception=False):
    return check_permission(person, "base.delete_educationgroup", raise_exception) and \
           _is_eligible_education_group(person, education_group, raise_exception)


def is_education_group_creation_period_opened(raise_exception=False):
    result = academic_calendar.is_academic_calendar_opened(academic_calendar_type.EDUCATION_GROUP_EDITION)
    can_raise_exception(raise_exception, result, "The education group edition period is not open.")

    return result


def _is_eligible_education_group(person, education_group, raise_exception):
    return (
            check_link_to_management_entity(education_group, person, raise_exception) and
            (
                    person.is_central_manager() or is_education_group_creation_period_opened(raise_exception)
            )
    )


def check_link_to_management_entity(education_group, person, raise_exception):
    if education_group:
        eligible_entities = get_education_group_year_update_eligible_entities(education_group)
        result = person.is_attached_entities(eligible_entities)
    else:
        result = True

    can_raise_exception(raise_exception, result, "The user is not attached to the management entity")

    return result


def check_permission(person, permission, raise_exception=False):
    result = person.user.has_perm(permission)
    can_raise_exception(raise_exception, result, ERRORS_MSG.get(permission, ""))

    return result


def can_raise_exception(raise_exception, result, msg):
    if raise_exception and not result:
        raise PermissionDenied(_(msg))


def check_authorized_type(education_group, category, raise_exception=False):
    if not education_group or not category:
        return True

    result = find_authorized_types(
        category=category,
        parents=[education_group]
    ).exists()

    parent_category = education_group.education_group_type.category
    can_raise_exception(
        raise_exception, result,
        pgettext(
            "female" if parent_category in [TRAINING, MINI_TRAINING] else "male",
            "No type of %(child_category)s can be created as child of %(category)s of type %(type)s"
        ) % {
            "child_category": _(category),
            "category": _(education_group.education_group_type.category),
            "type": education_group.education_group_type.name,
        })

    return result


def get_education_group_year_update_eligible_entities(education_group):
    if education_group and education_group.management_entity:
        return [education_group.management_entity]
    else:
        eligible_entities = []
        for group in group_element_year.find_by_child_branch(education_group).select_related('parent'):
            eligible_entities = eligible_entities + get_education_group_year_update_eligible_entities(group.parent)

        return eligible_entities
