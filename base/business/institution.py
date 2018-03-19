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
from base.models import entity_calendar, academic_calendar
from base.models.academic_year import current_academic_year
from base.models.enums import academic_calendar_type


def find_summary_course_submission_dates_for_entity_version(entity_version):
    current_entity_calendar_instance = None
    entity_vrs = entity_version
    while current_entity_calendar_instance is None and entity_vrs.get_parent_version():
        entity_vrs = entity_vrs.get_parent_version()
        current_entity_calendar_instance = entity_calendar.find_by_entity_and_reference_for_current_academic_year(
            entity_vrs.entity.id, academic_calendar_type.SUMMARY_COURSE_SUBMISSION)
    if current_entity_calendar_instance is None:
        current_entity_calendar_instance = academic_calendar.get_by_reference_and_academic_year(
            academic_calendar_type.SUMMARY_COURSE_SUBMISSION, current_academic_year())
    return {'start_date': current_entity_calendar_instance.start_date,
            'end_date': current_entity_calendar_instance.end_date}
