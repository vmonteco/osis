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

from django.db import IntegrityError
from django.db.models import F
from django.utils.translation import ugettext_lazy as _

from base.business.learning_unit import compute_max_academic_year_adjournment
from base.business.learning_unit_deletion import delete_from_given_learning_unit_year, \
    check_learning_unit_year_deletion
from base.models.academic_year import AcademicYear
from base.models.enums import learning_unit_periodicity
from base.models.learning_unit_year import LearningUnitYear


def edit_learning_unit_end_date(learning_unit_to_edit, new_academic_year):
    result = []

    new_end_year = _get_new_end_year(new_academic_year)
    end_year = _get_actual_end_year(learning_unit_to_edit)

    if not new_academic_year:  # If there is no selected academic_year, we take the maximal value
        new_academic_year = AcademicYear.objects.get(year=compute_max_academic_year_adjournment())

    if new_academic_year.year > end_year:
        result.extend(extend_learning_unit(learning_unit_to_edit, new_academic_year))
    elif new_academic_year.year < end_year:
        result.extend(shorten_learning_unit(learning_unit_to_edit, new_academic_year))

    result.append(_update_end_year_field(learning_unit_to_edit, new_end_year))
    return result


def shorten_learning_unit(learning_unit_to_edit, new_academic_year):
    learning_unit_year_to_delete = LearningUnitYear.objects.filter(
        learning_unit=learning_unit_to_edit,
        academic_year__year=new_academic_year.year + 1
    ).order_by('academic_year__start_date').first()

    if not learning_unit_year_to_delete:
        return []

    _check_partims(learning_unit_year_to_delete, new_academic_year)

    warning_msg = check_learning_unit_year_deletion(learning_unit_year_to_delete)
    if warning_msg:
        raise IntegrityError(list(warning_msg.values()))

    return delete_from_given_learning_unit_year(learning_unit_year_to_delete)


def extend_learning_unit(learning_unit_to_edit, new_academic_year):
    result = []
    last_learning_unit_year = LearningUnitYear.objects.filter(learning_unit=learning_unit_to_edit
                                                              ).order_by('academic_year').last()

    lu_parent = last_learning_unit_year.parent
    if last_learning_unit_year.subtype == 'PARTIM' and \
            lu_parent and lu_parent.learning_unit.end_year < new_academic_year.year:
        raise IntegrityError(_('The selected end year is greater than the end year of the parent %(lu_parent)s') % {
            'lu_parent': lu_parent
        })

    for ac_year in _get_next_academic_years(learning_unit_to_edit, new_academic_year.year):
        new_luy = _update_academic_year_for_learning_unit_year(last_learning_unit_year, ac_year)
        result.append(_('Learning unit %(learning_unit)s created for the academic year %(academic_year)s') % {
            'learning_unit': new_luy.acronym,
            'academic_year': new_luy.academic_year
        })

    return result


def _update_end_year_field(lu, year):
    lu.end_year = year
    lu.save()
    return _('Learning unit %(learning_unit)s has been updated successfully') % {'learning_unit': lu}


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


def _check_partims(learning_unit_year_to_delete, new_academic_year):
    partims = learning_unit_year_to_delete.get_partims_related() or []
    for partim in partims:
        if partim.learning_unit.end_year or partim.learning_unit.end_year <= new_academic_year.year:
            continue
        raise IntegrityError(
            _('The learning unit %(learning_unit)s has a partim %(partim)s with an end year greater than %(year)s') % {
                'learning_unit': learning_unit_year_to_delete.acronym,
                'partim': partim.acronym,
                'year': new_academic_year
            }
        )


def _get_actual_end_year(learning_unit_to_edit):
    return learning_unit_to_edit.end_year or compute_max_academic_year_adjournment()


def _get_new_end_year(new_academic_year):
    return new_academic_year.year if new_academic_year else None


def _get_next_academic_years(learning_unit_to_edit, year):
    range_years = list(range(learning_unit_to_edit.end_year + 1, year + 1))
    queryset = AcademicYear.objects.filter(year__in=range_years).order_by('year')
    return filter_biennial(queryset, learning_unit_to_edit.periodicity)


def filter_biennial(queryset, periodicity):
    result = queryset
    if periodicity != learning_unit_periodicity.ANNUAL:
        is_odd = periodicity == learning_unit_periodicity.BIENNIAL_ODD
        result = queryset.annotate(odd=F('year') % 2).filter(odd=is_odd)
    return result
