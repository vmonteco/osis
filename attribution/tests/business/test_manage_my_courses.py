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
from django.test import TestCase

from attribution.business.manage_my_courses import find_learning_unit_years_summary_editable
from attribution.business.perms import can_user_edit_educational_information
from attribution.tests.factories.attribution import AttributionFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.tutor import TutorFactory


class TestUserCanEditEducationalInformation(TestCase):
    def test_when_learning_unit_year_does_not_exist(self):
        an_attribution = AttributionFactory(summary_responsible=True, learning_unit_year__summary_editable=True)

        can_edit_educational_information = can_user_edit_educational_information(an_attribution.tutor.person.user,
                                                                                 an_attribution.learning_unit_year.id+1)
        self.assertFalse(can_edit_educational_information)

    def test_when_not_attributed_to_the_learning_unit_year(self):
        an_attribution = AttributionFactory(summary_responsible=True, learning_unit_year__summary_editable=True)
        an_other_attribution = AttributionFactory(summary_responsible=True, learning_unit_year__summary_editable=True)
        can_edit_educational_information = can_user_edit_educational_information(an_other_attribution.tutor.person.user,
                                                                                 an_attribution.learning_unit_year.id)
        self.assertFalse(can_edit_educational_information)

    def test_when_not_summary_responsible(self):
        can_edit_educational_information = \
            self.create_attribution_and_check_if_user_can_edit_educational_information(False, True)
        self.assertFalse(can_edit_educational_information)

    def test_when_summary_responsible_but_learning_unit_year_educational_information_cannot_be_edited(self):
        can_edit_educational_information =\
            self.create_attribution_and_check_if_user_can_edit_educational_information(True, False)
        self.assertFalse(can_edit_educational_information)

    def test_when_summary_responsible_and_learning_unit_year_educational_information_can_be_edited(self):
        can_edit_educational_information = \
            self.create_attribution_and_check_if_user_can_edit_educational_information(True, True)
        self.assertTrue(can_edit_educational_information)

    @staticmethod
    def create_attribution_and_check_if_user_can_edit_educational_information(summary_responsible, summary_editable):
        an_attribution = AttributionFactory(summary_responsible=summary_responsible,
                                            learning_unit_year__summary_editable=summary_editable)
        return can_user_edit_educational_information(an_attribution.tutor.person.user,
                                                     an_attribution.learning_unit_year.id)


class TestFindLearningUnitYearsSummaryEditable(TestCase):
    def setUp(self):
        self.tutor = TutorFactory()
        self.learning_unit_years = [LearningUnitYearFactory(summary_editable=True) for i in range(4)]
        self.attributions = [AttributionFactory(tutor=self.tutor,
                                                summary_responsible= True,
                                                learning_unit_year=self.learning_unit_years[i])
                             for i in range(4)]

    def test_when_summary_responsible_for_all_attributions_and_all_are_summary_editable(self):
        expected_luys = self.learning_unit_years
        actual_luys = find_learning_unit_years_summary_editable(self.tutor)
        self.assertCountEqual(expected_luys, list(actual_luys))

    def test_not_return_luy_which_are_not_summary_editable(self):
        self.learning_unit_years[0].summary_editable = False
        self.learning_unit_years[0].save()
        self.learning_unit_years[2].summary_editable = False
        self.learning_unit_years[2].save()

        expected_luys = [self.learning_unit_years[1], self.learning_unit_years[3]]
        actual_luys = find_learning_unit_years_summary_editable(self.tutor)
        self.assertCountEqual(expected_luys, list(actual_luys))

    def test_not_return_luy_for_which_tutor_is_not_summary_responsible(self):
        self.attributions[0].summary_responsible = False
        self.attributions[0].save()
        self.attributions[2].summary_responsible = False
        self.attributions[2].save()

        expected_luys = [self.learning_unit_years[1], self.learning_unit_years[3]]
        actual_luys = find_learning_unit_years_summary_editable(self.tutor)
        self.assertCountEqual(expected_luys, list(actual_luys))

    def test_not_return_luy_which_are_not_summary_editable_and_for_wich_tutor_is_not_summary_responsible(self):
        self.attributions[0].summary_responsible = False
        self.attributions[0].save()
        self.attributions[2].summary_responsible = False
        self.attributions[2].save()

        self.attributions[0].summary_responsible = False
        self.attributions[0].save()
        self.attributions[2].summary_responsible = False
        self.attributions[2].save()

        expected_luys = [self.learning_unit_years[1], self.learning_unit_years[3]]
        actual_luys = find_learning_unit_years_summary_editable(self.tutor)
        self.assertCountEqual(expected_luys, list(actual_luys))
