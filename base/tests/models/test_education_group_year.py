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
import datetime
from django.test import TestCase
from base.models.education_group_year import *
from base.tests.factories.academic_year import AcademicYearFactory

from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.education_group_year import EducationGroupTypeFakerFactory


class EducationGroupYearTest(TestCase):
    def setUp(self):
        academic_year = AcademicYearFactory()
        self.education_group_type_1 = EducationGroupTypeFakerFactory()
        self.education_group_type_2 = EducationGroupTypeFakerFactory()
        self.education_group_year_1 = EducationGroupYearFactory(academic_year=academic_year,
                                                                education_group_type=self.education_group_type_1)
        self.education_group_year_2 = EducationGroupYearFactory(academic_year=academic_year,
                                                                education_group_type=self.education_group_type_2)
        self.education_group_year_2.save()

    def test_find_by_id(self):
        education_group_year = find_by_id(self.education_group_year_1.id)
        self.assertEqual(education_group_year, self.education_group_year_1)

        education_group_year = find_by_id(-1)
        self.assertIsNone(education_group_year)

    def test_search(self):
        result = search(id=[self.education_group_year_1.id, self.education_group_year_2.id])
        self.assertEqual(len(result), 2)

        result = search(education_group_type=self.education_group_year_2.education_group_type)
        self.assertEqual(result.first().education_group_type, self.education_group_year_2.education_group_type)

    def test_properties_none(self):
        domains = self.education_group_year_1.domains
        self.assertEqual(domains, '')

        administration_entity = self.education_group_year_1.administration_entity
        self.assertIsNone(administration_entity)

        management_entity = self.education_group_year_1.management_entity
        self.assertIsNone(management_entity)

        parent_by_training = self.education_group_year_1.parent_by_training
        self.assertIsNone(parent_by_training)

        children_by_group_element_year = self.education_group_year_1.children_by_group_element_year
        self.assertListEqual(children_by_group_element_year, [])