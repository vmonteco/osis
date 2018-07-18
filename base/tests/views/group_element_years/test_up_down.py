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
from unittest import mock

from django.contrib.auth.models import Permission
from django.http import HttpResponse
from django.http import HttpResponseForbidden
from django.http import HttpResponseNotAllowed
from django.http import HttpResponseNotFound
from django.test import TestCase
from django.urls import reverse
from waffle.testutils import override_flag

from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.group_element_year import GroupElementYearFactory
from base.tests.factories.person import CentralManagerFactory


@override_flag('education_group_update', active=True)
class TestUp(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.education_group_year = EducationGroupYearFactory()
        # Create contents of education group years [3 elements]
        cls.group_element_year_1 = GroupElementYearFactory(parent=cls.education_group_year)
        cls.group_element_year_2 = GroupElementYearFactory(parent=cls.education_group_year)
        cls.group_element_year_3 = GroupElementYearFactory(parent=cls.education_group_year)

        cls.person = CentralManagerFactory()
        cls.person.user.user_permissions.add(Permission.objects.get(codename="can_access_education_group"))
        cls.url = reverse(
            "group_element_year_management",
            kwargs={
                "root_id": cls.education_group_year.id,
                "education_group_year_id": cls.education_group_year.id,
                "group_element_year_id": cls.group_element_year_3.id
            }
        )
        cls.post_valid_data = {'action': 'up'}

    def setUp(self):
        self.client.force_login(self.person.user)

    def test_up_case_user_not_logged(self):
        self.client.logout()
        response = self.client.post(self.url, self.post_valid_data)

        self.assertRedirects(response, '/login/?next={}'.format(self.url))

    @override_flag('education_group_update', active=False)
    def test_up_case_flag_disabled(self):
        response = self.client.post(self.url, self.post_valid_data)
        self.assertEqual(response.status_code, HttpResponseNotFound.status_code)
        self.assertTemplateUsed(response, "page_not_found.html")

    @mock.patch("base.views.education_groups.perms.can_change_education_group", side_effect=lambda user: False)
    def test_up_case_user_not_have_access(self, mock_permission):
        response = self.client.post(self.url, self.post_valid_data)
        self.assertEqual(response.status_code, HttpResponseForbidden.status_code)
        self.assertTemplateUsed(response, "access_denied.html")

    @mock.patch("base.business.education_groups.perms.is_eligible_to_change_education_group")
    def test_up_case_method_not_allowed(self, mock_permission):
        mock_permission.return_value = True
        response = self.client.get(self.url, data=self.post_valid_data)
        self.assertEqual(response.status_code, HttpResponseNotAllowed.status_code)

    @mock.patch("base.models.group_element_year.GroupElementYear.up")
    @mock.patch("base.business.education_groups.perms.is_eligible_to_change_education_group")
    def test_up_case_success(self, mock_permission, mock_up):
        mock_permission.return_value = True
        response = self.client.post(self.url, data=self.post_valid_data, follow=True)
        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertTrue(mock_up.called)


@override_flag('education_group_update', active=True)
class TestDown(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.education_group_year = EducationGroupYearFactory()
        # Create contents of education group years [3 elements]
        cls.group_element_year_1 = GroupElementYearFactory(parent=cls.education_group_year)
        cls.group_element_year_2 = GroupElementYearFactory(parent=cls.education_group_year)
        cls.group_element_year_3 = GroupElementYearFactory(parent=cls.education_group_year)

        cls.person = CentralManagerFactory()
        cls.person.user.user_permissions.add(Permission.objects.get(codename="can_access_education_group"))
        cls.url = reverse(
            "group_element_year_management",
            kwargs={
                "root_id": cls.education_group_year.id,
                "education_group_year_id": cls.education_group_year.id,
                "group_element_year_id": cls.group_element_year_1.id
            }
        )
        cls.post_valid_data = {'action': 'down'}

    def setUp(self):
        self.client.force_login(self.person.user)

    def test_down_case_user_not_logged(self):
        self.client.logout()
        response = self.client.post(self.url, self.post_valid_data)

        self.assertRedirects(response, '/login/?next={}'.format(self.url))

    @override_flag('education_group_update', active=False)
    def test_down_case_flag_disabled(self):
        response = self.client.post(self.url, self.post_valid_data)
        self.assertEqual(response.status_code, HttpResponseNotFound.status_code)
        self.assertTemplateUsed(response, "page_not_found.html")

    @mock.patch("base.views.education_groups.perms.can_change_education_group", side_effect=lambda user: False)
    def test_down_case_user_not_have_access(self, mock_permission):
        response = self.client.post(self.url, self.post_valid_data)
        self.assertEqual(response.status_code, HttpResponseForbidden.status_code)
        self.assertTemplateUsed(response, "access_denied.html")

    @mock.patch("base.business.education_groups.perms.is_eligible_to_change_education_group")
    def test_down_case_method_not_allowed(self, mock_permission):
        mock_permission.return_value = True
        response = self.client.get(self.url, data=self.post_valid_data)
        self.assertEqual(response.status_code, HttpResponseNotAllowed.status_code)

    @mock.patch("base.models.group_element_year.GroupElementYear.down")
    @mock.patch("base.business.education_groups.perms.is_eligible_to_change_education_group")
    def test_down_case_success(self, mock_permission, mock_down):
        mock_permission.return_value = True
        response = self.client.post(self.url, data=self.post_valid_data, follow=True)
        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertTrue(mock_down.called)
