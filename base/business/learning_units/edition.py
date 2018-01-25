##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2017 Université catholique de Louvain (http://www.uclouvain.be)
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
import uuid

from django.utils.translation import ugettext_lazy as _

from base.business.learning_unit_deletion import can_delete_learning_unit_year, delete_from_given_learning_unit_year
from base.business.learning_unit_proposal import is_person_linked_to_entity_in_charge_of_learning_unit
from base.models import proposal_learning_unit
from base.models.academic_year import AcademicYear
from base.models.learning_unit import is_old_learning_unit
from base.models.learning_unit_year import LearningUnitYear
from base.utils.send_mail import send_mail_after_the_learning_unit_year_deletion


def is_eligible_for_modification_end_date(learning_unit_year, a_person):
    """
    A learning unit end date can be editable only under some conditions:
        - It cannot be in the past
        - It cannot be in a proposal state
        - The user have the right to edit it
    """
    result = False
    if is_old_learning_unit(learning_unit_year.learning_unit):
        pass
    elif proposal_learning_unit.find_by_learning_unit_year(learning_unit_year):
        pass
    elif is_person_linked_to_entity_in_charge_of_learning_unit(learning_unit_year, a_person):
        result = True
    return result


def change_learning_unit_end_date(learning_unit_to_edit, new_academic_year, user):
    """
    Decide to extend or shorten the learning unit
    """
    result = []
    if new_academic_year.year > learning_unit_to_edit.end_year:
        result = extend_learning_unit(learning_unit_to_edit, new_academic_year)
    elif new_academic_year.year < learning_unit_to_edit.end_year:
        result = shorten_learning_unit(learning_unit_to_edit, new_academic_year, user)

    return result


def shorten_learning_unit(learning_unit_to_edit, new_academic_year, user):
    """
    Delete existing learning_unit_years above a given academic_year
    """
    learning_unit_year_to_delete = LearningUnitYear.objects.filter(
        learning_unit=learning_unit_to_edit,
        academic_year__year=new_academic_year.year + 1
    ).order_by('academic_year__start_date').first()

    result = []
    if learning_unit_year_to_delete:

        if not can_delete_learning_unit_year(user, learning_unit_year_to_delete):
            return

        result.extend(delete_from_given_learning_unit_year(learning_unit_year_to_delete))

        send_mail_after_the_learning_unit_year_deletion([],
                                                        learning_unit_year_to_delete.acronym,
                                                        learning_unit_year_to_delete.academic_year,
                                                        result)

    else:
        # The learning_unit does not have learning_unit_year
        # We can simply update end_year field
        learning_unit_to_edit.end_year = new_academic_year.year
        learning_unit_to_edit.save()
        result.append(
            _('Learning unit %(learning_unit)s has been updated successfully') % {
                'learning_unit': learning_unit_to_edit
            }
        )

    return result


def extend_learning_unit(learning_unit_to_edit, new_academic_year):
    """
    Create new learning_unit_years until a given academic_year
    """
    result = []
    last_learning_unit_year = LearningUnitYear.objects.filter(learning_unit=learning_unit_to_edit
                                                              ).order_by('academic_year').last()

    range_years = list(range(learning_unit_to_edit.end_year + 1, new_academic_year.year + 1))

    for ac_year in AcademicYear.objects.filter(year__in=range_years).order_by('year'):
        new_luy = _update_academic_year_for_learning_unit_year(last_learning_unit_year, ac_year)
        result.append(_('Learning unit created %(learning_unit)s for the academic year %(academic_year)s') % {
            'learning_unit': new_luy.acronym,
            'academic_year': new_luy.academic_year
        })

    learning_unit_to_edit.end_year = new_academic_year.year
    learning_unit_to_edit.save()
    return result


def _duplicate_object(obj):
    obj.pk = None
    obj.uuid = uuid.uuid4()
    return obj


def _update_academic_year_for_learning_unit_year(luy, new_academic_year):
    duplicated_luy = _duplicate_object(luy)

    duplicated_luy.academic_year = new_academic_year
    duplicated_luy.learning_container_year = _update_academic_year_for_learning_container_year(
        duplicated_luy.learning_container_year, new_academic_year)

    duplicated_luy.save()

    return duplicated_luy


def _update_academic_year_for_learning_container_year(lcy, new_academic_year):
    duplicated_lcy = _duplicate_object(lcy)

    duplicated_lcy.academic_year = new_academic_year
    duplicated_lcy.save()

    return duplicated_lcy
