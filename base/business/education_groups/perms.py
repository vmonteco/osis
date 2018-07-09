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

from base.models import academic_calendar
from base.models.enums import academic_calendar_type
from osis_common.utils.perms import conjunction, disjunction


def is_eligible_to_add_education_group(person):
    return conjunction(
            has_person_the_right_to_add_education_group,
            disjunction(is_central_manager, is_education_group_creation_period_opened),
    )(person)


def is_eligible_to_change_education_group(person):
    return conjunction(
        has_person_the_right_to_change_education_group,
        disjunction(is_central_manager, is_education_group_creation_period_opened),
    )(person)


def is_eligible_to_delete_education_group(person, raise_exception=False):
    return has_person_the_right_to_delete_education_group(person, raise_exception) and (
            person.is_central_manager() or
            is_education_group_creation_period_opened(person, raise_exception)
    )


def is_central_manager(person):
    return person.is_central_manager()


def is_education_group_creation_period_opened(person, raise_exception=False):
    result = academic_calendar.is_academic_calendar_opened(academic_calendar_type.EDUCATION_GROUP_EDITION)

    if raise_exception and not result:
        raise PermissionDenied("The education group edition period is not open.")

    return result


def has_person_the_right_to_add_education_group(person):
    return person.user.has_perm('base.add_educationgroup')


def has_person_the_right_to_change_education_group(person):
    return person.user.has_perm('base.change_educationgroup')


def has_person_the_right_to_delete_education_group(person, raise_exception=False):
    result = person.user.has_perm('base.delete_educationgroup')

    if raise_exception and not result:
        raise PermissionDenied("User has not permission to delete education groups.")

    return result
