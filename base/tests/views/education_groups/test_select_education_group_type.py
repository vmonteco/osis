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
from unittest import mock

from django.test import TestCase
from django.urls import reverse
from waffle.testutils import override_flag

from base.models.enums import education_group_categories
from base.tests.factories.education_group_type import EducationGroupTypeFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.person import PersonFactory


@override_flag('education_group_create', active=True)
class TestSelectEducationGroupTypeView(TestCase):

    def setUp(self):
        self.parent_education_group_year = EducationGroupYearFactory()

        self.test_categories = [
            education_group_categories.GROUP,
            education_group_categories.TRAINING,
            education_group_categories.MINI_TRAINING,
        ]

        self.education_group_types = [
            EducationGroupTypeFactory(category=category)
            for category in self.test_categories
        ]

        self.person = PersonFactory()

        self.client.force_login(self.person.user)
        self.perm_patcher = mock.patch("base.business.education_groups.perms._is_eligible_to_add_education_group",
                                       return_value=True)
        self.mocked_perm = self.perm_patcher.start()

    def tearDown(self):
        self.perm_patcher.stop()

    def test_get(self):
        response = self.client.get(
            reverse(
                "select_education_group_type",
                args=[self.test_categories[0]]
            )
        )
        self.assertTemplateUsed(response, "education_group/blocks/form/education_group_type.html")

    def test_post(self):
        response = self.client.post(
            reverse(
                "select_education_group_type",
                args=[self.test_categories[0]]
            ), data={"name": self.education_group_types[0].pk}
        )

        self.assertRedirects(
            response,
            reverse(
                "new_education_group", args=[self.test_categories[0], self.education_group_types[0].pk]
            )
        )

    def test_post_invalid(self):
        response = self.client.post(
            reverse(
                "select_education_group_type",
                args=[self.test_categories[0]]
            ), data={"name": self.education_group_types[1].pk}
        )
        self.assertEqual(len(response.context["form"].errors), 1)
