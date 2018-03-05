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

from attribution.business.manage_my_courses import can_user_edit_educational_information
from attribution.tests.factories.attribution import AttributionFactory


class TestUserCanEditEducationalInformation(TestCase):
    def test_when_not_summary_responsible(self):
        can_edit_educational_information = self.meth(False, True)
        self.assertFalse(can_edit_educational_information)

    def test_when_summary_responsible_but_learning_unit_year_educational_information_cannot_be_edited(self):
        can_edit_educational_information = self.meth(True, False)
        self.assertFalse(can_edit_educational_information)

    def test_when_summary_responsible_and_learning_unit_year_educational_information_can_be_edited(self):
        can_edit_educational_information = self.meth(True, True)
        self.assertTrue(can_edit_educational_information)

    @staticmethod
    def meth(summary_responsible, summary_editable):
        an_attribution = AttributionFactory(summary_responsible=summary_responsible,
                                            learning_unit_year__summary_editable=summary_editable)
        return can_user_edit_educational_information(an_attribution.tutor.person.user,
                                                     an_attribution.learning_unit_year.id)