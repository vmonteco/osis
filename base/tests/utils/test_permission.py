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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
import datetime
from django.test import TestCase
from base.utils import permission
from base.models.enums import academic_calendar_type
from django.contrib.auth.models import User
from base.tests.factories.academic_year import AcademicYearFactory, AcademicYearFakerFactory
from base.tests.factories.academic_calendar import AcademicCalendarFactory
from django.utils import timezone


now = timezone.now()

CURRENT_YEAR = now.year
NEXT_YEAR = now.year + 1

start_date = timezone.now().date()
end_date = start_date.replace(year=start_date.year + 1)
YEAR_CALENDAR = timezone.now().year


class TestPermission(TestCase):

    def setUp(self):
        self.a_user = User.objects.create_user(username='legat', email='legat@localhost', password='top_secret')

    def test_permission_is_undefined_no_academic_year(self):
        self.assertEqual(permission.is_summary_submission_opened(self.a_user), False)

    def test_permission_is_undefined_no_academic_calendar(self):
        AcademicYearFactory(year=timezone.now().year,
                            start_date=start_date,
                            end_date=end_date)
        self.assertEqual(permission.is_summary_submission_opened(self.a_user), False)

    def test_summary_submission_period_opened(self):
        current_academic_year = AcademicYearFakerFactory(start_date=timezone.now() - datetime.timedelta(days=10),
                                                    end_date=timezone.now() + datetime.timedelta(days=10))

        AcademicCalendarFactory(academic_year=current_academic_year,
                                reference=academic_calendar_type.SUMMARY_COURSE_SUBMISSION)
        self.assertTrue(permission.is_summary_submission_opened(self.a_user))

    def test_summary_submission_period_closed(self):

        current_academic_year = AcademicYearFactory(year=timezone.now().year,
                                                    start_date=timezone.now(),
                                                    end_date=timezone.now() + datetime.timedelta(days=1))

        today_plus_3_days = timezone.now() + datetime.timedelta(days=3)

        AcademicCalendarFactory.build(academic_year=current_academic_year,
                                      reference="A calendar event",
                                      start_date=today_plus_3_days,
                                      end_date=today_plus_3_days)
        self.assertFalse(permission.is_summary_submission_opened(self.a_user))
