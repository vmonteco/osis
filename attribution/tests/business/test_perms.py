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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
import datetime
from unittest import mock

from django.test import TestCase

from attribution.business.perms import _is_tutor_attributed_to_the_learning_unit, \
    _is_tutor_summary_responsible_of_learning_unit_year, _is_learning_unit_year_summary_editable, \
    _is_calendar_opened_to_edit_educational_information
from attribution.tests.factories.attribution import AttributionFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from osis_common.utils.datetime import get_tzinfo


class TestPerms(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.attribution = AttributionFactory(summary_responsible=True,
                                             learning_unit_year__summary_locked=False)
        cls.tutor = cls.attribution.tutor
        cls.learning_unit_year = cls.attribution.learning_unit_year

    def setUp(self):
        pass


    def test_is_tutor_attributed_to_the_learning_unit(self):
        learning_unit_year_not_attributed = LearningUnitYearFactory()
        self.assertFalse(_is_tutor_attributed_to_the_learning_unit(self.tutor.person.user,
                                                                  learning_unit_year_not_attributed.id))
        self.assertTrue(_is_tutor_attributed_to_the_learning_unit(self.tutor.person.user,
                                                                  self.learning_unit_year.id))

    def test_is_tutor_summary_responsible_of_learning_unit_year(self):
        attribution_not_summary_responsible = AttributionFactory(tutor=self.tutor)
        luy = attribution_not_summary_responsible.learning_unit_year
        self.assertFalse(_is_tutor_summary_responsible_of_learning_unit_year(self.tutor.person.user,
                                                                             luy.id))

        self.assertTrue(_is_tutor_summary_responsible_of_learning_unit_year(self.tutor.person.user,
                                                                            self.learning_unit_year.id))

    def test_is_learning_unit_year_summary_editable(self):
        luy_not_editable = LearningUnitYearFactory(summary_locked=True)
        self.assertFalse(_is_learning_unit_year_summary_editable(None, luy_not_editable.id))

        self.assertTrue(_is_learning_unit_year_summary_editable(None, self.learning_unit_year.id))

    def test_is_calendar_opened_to_edit_educational_information(self):
        patcher = mock.patch(
            'attribution.business.perms.find_educational_information_submission_dates_of_learning_unit_year')
        MockClass = patcher.start()

        today = datetime.datetime.now(tz=get_tzinfo())
        yesterday = today - datetime.timedelta(days=1)
        tomorrow = today + datetime.timedelta(days=1)

        MockClass.return_value = {}
        self.assertFalse(_is_calendar_opened_to_edit_educational_information(None,
                                                                             self.learning_unit_year.id))

        MockClass.return_value = {"start_date": yesterday,
                                  "end_date": yesterday}
        self.assertFalse(_is_calendar_opened_to_edit_educational_information(None,
                                                                             self.learning_unit_year.id))
        MockClass.return_value = {"start_date": tomorrow,
                                  "end_date": tomorrow}
        self.assertFalse(_is_calendar_opened_to_edit_educational_information(None,
                                                                             self.learning_unit_year.id))

        MockClass.return_value = {"start_date": today - datetime.timedelta(days=1),
                                  "end_date": today + datetime.timedelta(days=1)}
        self.assertTrue(_is_calendar_opened_to_edit_educational_information(None,
                                                                            self.learning_unit_year.id))

        patcher.stop()
