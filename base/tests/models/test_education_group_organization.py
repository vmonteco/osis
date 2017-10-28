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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django.test import TestCase
from base.models.education_group_organization import *

from base.tests.factories.education_group_organization import EducationGroupOrganizationFactory


class EducationGroupOrganization(TestCase):
    def setUp(self):
        self.education_group_organization = EducationGroupOrganizationFactory()
        self.education_group_organization.save()

    def test_search(self):
        education_group_organization = search(education_group_year=self.education_group_organization.education_group_year)
        self.assertEqual(education_group_organization.first().education_group_year,
                         self.education_group_organization.education_group_year)

        education_group_organization = search(education_group_year=-1)
        self.assertIsNone(education_group_organization.first())

        education_group_organization = search(not_education_group_year=-1)
        self.assertFalse(education_group_organization)

