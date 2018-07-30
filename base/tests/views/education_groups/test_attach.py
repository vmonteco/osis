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

from http import HTTPStatus
from unittest import mock
from unittest.mock import patch

from dateutil.utils import today
from django.test import TestCase, Client
from django.urls import reverse
from waffle.testutils import override_flag

from base.models.group_element_year import GroupElementYear
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.group_element_year import GroupElementYearFactory
from base.tests.factories.person import PersonFactory
from base.utils.cache import cache
from base.views.education_groups import select


@override_flag('education_group_attach', active=True)
@override_flag('education_group_select', active=True)
@override_flag('education_group_update', active=True)
class TestAttach(TestCase):

    def setUp(self):
        self.locmem_cache = cache
        self.locmem_cache.clear()
        self.patch = patch.object(select, 'cache', self.locmem_cache)
        self.patch.start()

        self.person = PersonFactory()
        self.client = Client()
        self.client.force_login(self.person.user)
        self.perm_patcher = mock.patch("base.business.education_groups.perms.is_eligible_to_change_education_group",
                                       return_value=True)
        self.mocked_perm = self.perm_patcher.start()

        self.academic_year = AcademicYearFactory(year=today().year)
        self.child_education_group_year = EducationGroupYearFactory(academic_year=self.academic_year)
        self.initial_parent_education_group_year = EducationGroupYearFactory(academic_year=self.academic_year)
        self.new_parent_education_group_year = EducationGroupYearFactory(academic_year=self.academic_year)

        self.initial_group_element_year = GroupElementYearFactory(
            parent=self.initial_parent_education_group_year,
            child_branch=self.child_education_group_year
        )

        self.url_select = reverse("education_group_select", args=[self.child_education_group_year.id])
        self.url_attach = reverse(
            "group_element_year_management",
            args=[
                self.new_parent_education_group_year.id,
                self.new_parent_education_group_year.id,
                self.initial_group_element_year.id,
        ]
        ) + "?action=attach"

        cache.set('child_to_cache_id', None, timeout=None)

    def tearDown(self):
        cache.set('child_to_cache_id', None, timeout=None)
        self.patch.stop()
        self.client.logout()
        self.perm_patcher.stop()

    def test_select(self):
        response = self.client.get(
            self.url_select,
            data={'child_to_cache_id': self.child_education_group_year.id},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        child_id = int(cache.get('child_to_cache_id'))

        self.assertEquals(response.status_code, HTTPStatus.OK)
        self.assertEquals(child_id, self.child_education_group_year.id)

    def test_attach(self):
        expected_absent_group_element_year = GroupElementYear.objects.filter(
            parent=self.new_parent_education_group_year,
            child_branch=self.child_education_group_year
        ).exists()
        self.assertFalse(expected_absent_group_element_year)

        self._assert_link_with_inital_parent_present()

        self.client.get(self.url_select, data={'child_to_cache_id' : self.child_education_group_year.id})
        self.client.get(self.url_attach, HTTP_REFERER='http://foo/bar')


        expected_group_element_year_count = GroupElementYear.objects.filter(
            parent=self.new_parent_education_group_year,
            child_branch=self.child_education_group_year
        ).count()
        self.assertEquals(expected_group_element_year_count, 1)

        self._assert_link_with_inital_parent_present()

    def _assert_link_with_inital_parent_present(self):
        expected_initial_group_element_year = GroupElementYear.objects.get(
            parent=self.initial_parent_education_group_year,
            child_branch=self.child_education_group_year
        )
        self.assertEquals(expected_initial_group_element_year, self.initial_group_element_year)
