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
from base.business.learning_unit_proposal import is_person_linked_to_entity_in_charge_of_learning_unit
from base.models import proposal_learning_unit
from base.models.academic_year import current_academic_year
from base.models.enums import learning_container_year_types


def is_eligible_for_modification_end_date(learning_unit_year, a_person):
    current_year = current_academic_year().year
    year = learning_unit_year.academic_year.year
    if year < current_year:
        return False
    if learning_unit_year.learning_container_year.container_type not in (learning_container_year_types.COURSE,
                                                                         learning_container_year_types.DISSERTATION,
                                                                         learning_container_year_types.INTERNSHIP):
        return False
    if proposal_learning_unit.find_by_learning_unit_year(learning_unit_year):
        return False
    return is_person_linked_to_entity_in_charge_of_learning_unit(learning_unit_year, a_person)

