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
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db import transaction, Error

from base.business.education_groups.postponement import duplicate_education_group_year, ConsistencyError
from base.models.academic_year import compute_max_academic_year_adjournment, AcademicYear
from base.models.education_group_year import EducationGroupYear
from base.models.enums.education_group_categories import GROUP
from base.utils.send_mail import send_mail_before_annual_procedure_of_automatic_postponement, \
    send_mail_after_annual_procedure_of_automatic_postponement


def fetch_education_group_to_postpone(queryset=None):
    if not queryset:
        queryset = EducationGroupYear.objects.all()

    # Fetch N+6 and N+5 academic_years
    last_academic_year = AcademicYear.objects.get(year=compute_max_academic_year_adjournment())
    penultimate_academic_year = last_academic_year.past()

    # We take all education group years from N+5 academic year
    # GROUP category does not need to be postpone
    qs_egy = queryset.filter(academic_year=penultimate_academic_year).exclude(education_group_type__category=GROUP)

    # Create filters to know which egys must be copied to N+6
    egys_already_duplicated = qs_egy.filter(education_group__educationgroupyear__academic_year=last_academic_year)
    egys_to_not_duplicate = qs_egy.filter(education_group__end_year__lt=last_academic_year.year)
    egys_to_duplicate = qs_egy.difference(egys_already_duplicated, egys_to_not_duplicate)

    # send statistics to the managers
    send_mail_before_annual_procedure_of_automatic_postponement(last_academic_year, egys_to_duplicate,
                                                                egys_already_duplicated, egys_to_not_duplicate)

    result, errors = extend_education_groups_until_last_academic_year(last_academic_year, egys_to_duplicate)

    # send statistics with results to the managers
    send_mail_after_annual_procedure_of_automatic_postponement(last_academic_year, result, egys_already_duplicated,
                                                               egys_to_not_duplicate, errors)

    return result, errors


def extend_education_groups_until_last_academic_year(last_academic_year, egys_to_duplicate):
    result = []
    errors = []
    for egy in egys_to_duplicate:
        try:
            with transaction.atomic():
                result.append(duplicate_education_group_year(egy, last_academic_year))

        # General catch to be sure to not stop the rest of the duplication
        except (Error, ObjectDoesNotExist, MultipleObjectsReturned, ConsistencyError):
            errors.append(egy)

    return result, errors


MSG_RESULT = "%s education group(s) extended and %s error(s)"


def serialize_postponement_results(result, errors):
    return {
        "msg": MSG_RESULT % (len(result), len(errors)),
        "errors": [str(egy) for egy in errors]
    }
