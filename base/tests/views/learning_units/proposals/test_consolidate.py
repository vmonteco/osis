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

from django.http import HttpResponseNotAllowed, HttpResponseForbidden, HttpResponseNotFound
from django.test import TestCase
from rest_framework.reverse import reverse

from base.tests.factories.person import PersonFactory
from base.tests.factories.proposal_learning_unit import ProposalLearningUnitFactory


class TestConsolidate(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.learning_unit_year = ProposalLearningUnitFactory().learning_unit_year
        cls.url = reverse("learning_unit_consolidate_proposal", args=[cls.learning_unit_year.id])
        cls.person = PersonFactory()

    def setUp(self):
        self.client.force_login(self.person.user)

    def test_login_required(self):
        self.client.logout()

        response = self.client.get(self.url)

        self.assertRedirects(response, "/login/?next={}".format(self.url))

    def test_accepts_only_post_request(self):
        response = self.client.get(self.url)

        self.assertTemplateUsed(response, "method_not_allowed.html")
        self.assertEqual(response.status_code, HttpResponseNotAllowed.status_code)

    @mock.patch("base.business.learning_units.perms.is_eligible_to_consolidate_proposal",
                side_effect=lambda prop, pers: False)
    def test_when_no_permission_to_consolidate(self, mock_perm):
        response = self.client.post(self.url)

        self.assertTemplateUsed(response, "access_denied.html")
        self.assertEqual(response.status_code, HttpResponseForbidden.status_code)
        self.assertTrue(mock_perm.called)

    def test_when_no_proposal(self):
        url = reverse("learning_unit_consolidate_proposal", args=[self.learning_unit_year.id + 1])

        response = self.client.post(url)

        self.assertTemplateUsed(response, "page_not_found.html")
        self.assertEqual(response.status_code, HttpResponseNotFound.status_code)
