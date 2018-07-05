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
from waffle.testutils import override_flag

from base.models.education_group_year import EducationGroupYear
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.person import PersonFactory


@override_flag('education_group_delete', active=True)
class TestDeleteGroupEducationYearView(TestCase):

    def setUp(self):
        self.education_group_year = EducationGroupYearFactory()
        self.person = PersonFactory()
        self.url = reverse('delete_education_group', args=[self.education_group_year.id])

        self.person.user.user_permissions.add(Permission.objects.get(codename="delete_educationgroupyear"))
        self.client.force_login(user=self.person.user)

    def test_delete_get_permission_denied(self):
        self.person.user.user_permissions.remove(Permission.objects.get(codename="delete_educationgroupyear"))
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_delete_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_delete_post(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(EducationGroupYear.objects.filter(pk=self.education_group_year.pk).exists())
