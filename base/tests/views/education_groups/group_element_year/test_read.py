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
from django.http import HttpResponseRedirect
from django.test import TestCase
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.group_element_year import GroupElementYearFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.user import SuperUserFactory
from base.views.education_groups.group_element_year.read import get_verbose_children


class TestRead(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.person = PersonFactory()
        cls.education_group_year_1 = EducationGroupYearFactory()
        cls.education_group_year_2 = EducationGroupYearFactory()
        cls.education_group_year_3 = EducationGroupYearFactory()
        cls.learning_unit_year_1 = LearningUnitYearFactory()
        cls.learning_unit_year_2 = LearningUnitYearFactory()
        cls.group_element_year_1 = GroupElementYearFactory(parent=cls.education_group_year_1,
                                                           child_branch=cls.education_group_year_2)
        cls.group_element_year_2 = GroupElementYearFactory(parent=cls.education_group_year_2,
                                                           child_branch=None,
                                                           child_leaf=cls.learning_unit_year_1)
        cls.group_element_year_3 = GroupElementYearFactory(parent=cls.education_group_year_1,
                                                           child_branch=cls.education_group_year_3)
        cls.group_element_year_4 = GroupElementYearFactory(parent=cls.education_group_year_3,
                                                           child_branch=None,
                                                           child_leaf=cls.learning_unit_year_2)
        cls.a_superuser = SuperUserFactory()

    def test_pdf_content(self):
        url = reverse("pdf_content", args=[self.education_group_year_1.id, self.education_group_year_1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, HttpResponseRedirect.status_code)

    def test_get_verbose_children(self):
        result = get_verbose_children(self.education_group_year_1)
        context_waiting = [self.group_element_year_1, [self.group_element_year_2], self.group_element_year_3,
                           [self.group_element_year_4]]
        self.assertEqual(result, context_waiting)
