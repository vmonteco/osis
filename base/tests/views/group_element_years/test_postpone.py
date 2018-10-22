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

from django.test import TestCase
from django.urls import reverse
from waffle.testutils import override_flag

from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.group_element_year import GroupElementYearFactory
from base.tests.factories.person import CentralManagerFactory


@override_flag('education_group_update', active=True)
class TestPostpone(TestCase):

    def setUp(self):
        self.person = CentralManagerFactory()
        self.client.force_login(self.person.user)
        self.education_group_year = EducationGroupYearFactory()
        self.group_element_year = GroupElementYearFactory(parent=self.education_group_year)
        self.url = reverse(
            "postpone_education_group",
            kwargs={
                "root_id": self.education_group_year.pk,
                "education_group_year_id": self.education_group_year.pk,
            }
        )

    def test_postpone_case_user_not_logged(self):
        self.client.logout()
        response = self.client.get(self.url)

        self.assertRedirects(response, '/login/?next={}'.format(self.url))
