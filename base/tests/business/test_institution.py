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
import datetime

from django.test import TestCase

from base.business.institution import find_summary_course_submission_dates_for_entity_version
from base.models.enums import academic_calendar_type
from base.tests.factories.academic_calendar import AcademicCalendarFactory
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.entity import EntityFactory
from base.tests.factories.entity_calendar import EntityCalendarFactory
from base.tests.factories.entity_version import EntityVersionFactory


class FindSummaryCourseSubmissionDatesTestCase(TestCase):
    def setUp(self):
        today = datetime.date.today()
        self.current_academic_year = AcademicYearFactory(start_date=today,
                                                         end_date=today.replace(year=today.year + 1),
                                                         year=today.year)
        self.parent_entity = EntityFactory()
        self.child_entity = EntityFactory()
        self.academic_calendar = AcademicCalendarFactory(academic_year=self.current_academic_year,
                                                         reference=academic_calendar_type.SUMMARY_COURSE_SUBMISSION)
        self.parent_entity_version = EntityVersionFactory(start_date=self.current_academic_year.start_date,
                                                          end_date=self.current_academic_year.end_date,
                                                          entity=self.parent_entity)
        self.child_entity_version = EntityVersionFactory(start_date=self.current_academic_year.start_date,
                                                         end_date=self.current_academic_year.end_date,
                                                         entity=self.child_entity,
                                                         parent=self.parent_entity)
        self.entity_version_without_entity_calendar = EntityVersionFactory(start_date=self.current_academic_year.start_date,
                                                                           end_date=self.current_academic_year.end_date)
        self.parent_entity_calendar = EntityCalendarFactory(academic_calendar=self.academic_calendar,
                                                            entity=self.parent_entity)


    def test_when_parent_has_entity_calendar_instance(self):
        child_entity_dates = find_summary_course_submission_dates_for_entity_version(self.child_entity_version)
        self.assertEqual(child_entity_dates, {'start_date':self.parent_entity_calendar.start_date,
                                              'end_date':self.parent_entity_calendar.end_date})

    def test_when_no_parent_has_entity_calendar_instance(self):
        default_entity_dates = find_summary_course_submission_dates_for_entity_version(self.entity_version_without_entity_calendar)
        self.assertEqual(default_entity_dates, {'start_date':self.academic_calendar.start_date,
                                                'end_date':self.academic_calendar.end_date})
