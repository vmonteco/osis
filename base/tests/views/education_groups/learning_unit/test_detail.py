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
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.group_element_year import GroupElementYearFactory
from base.tests.factories.learning_component_year import LearningComponentYearFactory
from base.tests.factories.learning_unit_component import LearningUnitComponentFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.user import UserFactory


class TestDetail(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.person = PersonFactory()
        cls.education_group_year_1 = EducationGroupYearFactory(title_english="")
        cls.education_group_year_2 = EducationGroupYearFactory(title_english="")
        cls.education_group_year_3 = EducationGroupYearFactory(title_english="")
        cls.learning_unit_year_1 = LearningUnitYearFactory(specific_title_english="")
        cls.learning_unit_year_2 = LearningUnitYearFactory(specific_title_english="")
        cls.learning_component_year_1 = LearningComponentYearFactory(
            learning_container_year=cls.learning_unit_year_1.learning_container_year, hourly_volume_partial_q1=10,
            hourly_volume_partial_q2=10)
        cls.learning_component_year_2 = LearningComponentYearFactory(
            learning_container_year=cls.learning_unit_year_1.learning_container_year, hourly_volume_partial_q1=10,
            hourly_volume_partial_q2=10)
        cls.learning_unit_component_1 = LearningUnitComponentFactory(
            learning_component_year=cls.learning_component_year_1,
            learning_unit_year=cls.learning_unit_year_1)
        cls.learning_unit_component_2 = LearningUnitComponentFactory(
            learning_component_year=cls.learning_component_year_2,
            learning_unit_year=cls.learning_unit_year_1)
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
        cls.user = UserFactory()
        cls.person = PersonFactory(user=cls.user)
        cls.user.user_permissions.add(Permission.objects.get(codename="can_access_education_group"))

        cls.url = reverse(
            "learning_unit_utilization",
            args=[
                cls.education_group_year_1.id,
                cls.learning_unit_year_1.id,
            ]
        )

    def test_education_group_using_template_use(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'education_group/learning_unit/tab_utilization.html')

    def test_education_group_using_check_parent_list_with_group(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(len(response.context_data['group_element_years']), 1)
        self.assertTemplateUsed(response, 'education_group/learning_unit/tab_utilization.html')
