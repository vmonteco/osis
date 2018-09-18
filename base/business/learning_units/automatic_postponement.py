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
from django.db import transaction

from base.business.learning_units.edition import duplicate_learning_unit_year
from base.models.academic_year import compute_max_academic_year_adjournment, AcademicYear
from base.models.learning_unit_year import LearningUnitYear


# This method will be execute through a celery worker.
def fetch_learning_unit_to_postpone():
    """ Fetch all learning unit how need a postponement. """
    last_academic_year = AcademicYear.objects.get(year=compute_max_academic_year_adjournment())
    penultimate_academic_year = last_academic_year.past()

    # send statistics to the managers
    # List of UE to duplicate
    # List of UE not to be duplicated
    # List of UE already existing in N+6

    # We take all learning unit years from N+5 academic year
    qs_luy = LearningUnitYear.objects.filter(academic_year=penultimate_academic_year)
    # Create filters to know which luys must be copied to N+6
    luys_already_duplicated = qs_luy.filter(learning_unit__learningunityear__academic_year=last_academic_year)
    luys_to_not_duplicate = qs_luy.filter(learning_unit__end_year__lt=last_academic_year.year)
    luys_to_duplicate = qs_luy.difference(luys_already_duplicated, luys_to_not_duplicate)

    # Extend all learning unit until last_academic_year
    result = []

    for luy in luys_to_duplicate:
        with transaction.atomic():
            result.append(duplicate_learning_unit_year(luy, last_academic_year))

    # send statistics to the managers
    # List of UE to duplicate
    # List of UE not to be duplicated
    # List of UE already existing in N+6

    return result
