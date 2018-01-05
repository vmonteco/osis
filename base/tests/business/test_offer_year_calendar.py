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
from datetime import timedelta, datetime

from django.test import TestCase

from base.business.offer_year_calendar import compute_deadline_by_offer_year_calendar, _get_delta_deadline_tutor
from base.models.enums import academic_calendar_type
from base.models.session_exam_deadline import SessionExamDeadline
from base.tests.factories.academic_calendar import AcademicCalendarFactory
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.offer_enrollment import OfferEnrollmentFactory
from base.tests.factories.offer_year_calendar import OfferYearCalendarFactory
from base.tests.factories.session_exam_calendar import SessionExamCalendarFactory
from base.tests.factories.session_exam_deadline import SessionExamDeadlineFactory
from base.tests.factories.student import StudentFactory


class TestOfferYearCalendar(TestCase):

    def setUp(self):
        self.nb_session = 1

        self.academic_year = AcademicYearFactory(year=1950)
        # Create Academic calendar type DELIBERATION
        self.academic_calendar_deliberation = AcademicCalendarFactory.build(academic_year=self.academic_year,
                                                                            reference=academic_calendar_type.DELIBERATION)
        self.academic_calendar_deliberation.save(functions=[])

        self.session_exam_calendar = SessionExamCalendarFactory(academic_calendar=self.academic_calendar_deliberation,
                                                                number_session=self.nb_session)
        self.offer_year_calendar_deliberation = OfferYearCalendarFactory(academic_calendar=self.academic_calendar_deliberation)

        # Create Academic calendar type SCORES_EXAM_SUBMISSION
        self.ac_score_exam_submission = AcademicCalendarFactory.build(academic_year=self.academic_year,
                                                                      reference=academic_calendar_type.SCORES_EXAM_SUBMISSION)
        self.ac_score_exam_submission.save(functions=[])
        self.offer_year_calendar_submission = OfferYearCalendarFactory(academic_calendar=self.ac_score_exam_submission,
                                                                       education_group_year=self.offer_year_calendar_deliberation.education_group_year)

        self.students = [StudentFactory() for _ in range(10)]

        self.offer_enrollments = [
            OfferEnrollmentFactory(student=student, offer_year=self.offer_year_calendar_deliberation.offer_year)
            for student in self.students
        ]

        self.session_exam_deadlines = [
            SessionExamDeadlineFactory(offer_enrollment=offer_enrollment, number_session=self.nb_session)
            for offer_enrollment in self.offer_enrollments
        ]

    def test_compute_deadline_by_offer_year_calendar(self):
        self.session_exam_deadlines[0].deliberation_date = None
        self.session_exam_deadlines[0].save()

        correct_deadlines = [self.academic_calendar_deliberation.end_date - timedelta(days=1)
                             for _ in SessionExamDeadline.objects.all()]

        compute_deadline_by_offer_year_calendar(self.offer_year_calendar_deliberation)

        new_deadlines = [i.deadline for i in SessionExamDeadline.objects.all()]
        self.assertListEqual(new_deadlines, correct_deadlines)

    def test_compute_deadline_wrong_reference(self):
        self.offer_year_calendar_deliberation.academic_calendar.reference = academic_calendar_type.COURSE_ENROLLMENT
        old_deadlines = [i.deadline for i in self.session_exam_deadlines]

        compute_deadline_by_offer_year_calendar(self.offer_year_calendar_deliberation)

        new_deadlines = [i.deadline for i in SessionExamDeadline.objects.all()]

        self.assertListEqual(new_deadlines, old_deadlines)

    def test_compute_deadline_tutor_by_offer_year(self):
        """In this test, we will check if the tutor day delta [deadline is correctly computed] """
        pass

    def test_get_delta_deadline_tutor(self):
        today = datetime.today()
        fourty_day_before = today - timedelta(days=40)
        self.assertEqual(40, _get_delta_deadline_tutor(today, fourty_day_before))

    def test_get_delta_deadline_tutor_none_value(self):
        today = datetime.today()
        self.assertFalse(_get_delta_deadline_tutor(None, None))
        self.assertFalse(_get_delta_deadline_tutor(None, today))
        self.assertFalse(_get_delta_deadline_tutor(today, None))
