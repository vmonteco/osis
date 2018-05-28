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
from django.test import TestCase
from django.urls import reverse

from base.tests.factories.campus import CampusFactory
from base.tests.factories.organization_address import OrganizationAddressFactory
from base.views.learning_units.external.create import filter_campus_by_country
from reference.tests.factories.country import CountryFactory


class TestFilterCampusByCountry(TestCase):
    def setUp(self):
        self.country = CountryFactory()

        self.campuses = [CampusFactory() for _ in range(10)]

        self.organization_addresses = [
            OrganizationAddressFactory(organization=campus.organization)
            for campus in self.campuses
        ]

    def test_filter_campus_by_country(self):

        self.organization_addresses[0].country = self.country
        self.organization_addresses[0].save()

        campus = self.campuses[0]

        kwargs = {'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}
        url = reverse(filter_campus_by_country)

        get_data = {'country': self.country.pk,}

        response = self.client.get(url, get_data, **kwargs)
        self.assertJSONEqual(response.content.decode('utf-8'), [
            {
                'pk': campus.id, 'organization__name': campus.organization.name
             }])