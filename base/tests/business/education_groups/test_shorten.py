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

from base.business.education_groups import shorten
from base.models.education_group_year import EducationGroupYear
from base.models.enums import entity_type
from base.models.enums import organization_type
from base.tests.factories.academic_year import create_current_academic_year
from base.tests.factories.business.learning_units import GenerateAcademicYear
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.entity import EntityFactory
from base.tests.factories.entity_version import EntityVersionFactory


class EducationGroupShortenContextMixin(TestCase):
    """This mixin is used in this test file in order to setup an environment for testing EGY SHORTEN"""
    def setUp(self):
        # Create several academic year
        self.current_academic_year = create_current_academic_year()
        self.generated_ac_years = GenerateAcademicYear(self.current_academic_year.year + 1,
                                                       self.current_academic_year.year + 10)
        # Create small entities
        self.entity = EntityFactory(organization__type=organization_type.MAIN)
        self.entity_version = EntityVersionFactory(
            entity=self.entity,
            entity_type=entity_type.SECTOR
        )

        self.education_group_year = EducationGroupYearFactory(
            management_entity=self.entity,
            administration_entity=self.entity,
            academic_year=self.current_academic_year
        )


class TestStartShortenEducationGroupYear(EducationGroupShortenContextMixin):
    def test_start_shorten_case_no_deletion(self):
        # Remove all in the future
        EducationGroupYear.objects.filter(
            education_group=self.education_group_year.education_group,
            academic_year__year__gt=self.current_academic_year.year
        )

        result = shorten.start(self.education_group_year.education_group, self.current_academic_year.year)
        self.assertIsInstance(result, list)
        self.assertFalse(result)

    def test_start_shorten_case_multiple_deletion(self):
        # Insert multiple in future
        for ac_year in self.generated_ac_years.academic_years:
            EducationGroupYearFactory(
                education_group=self.education_group_year.education_group,
                management_entity=self.entity,
                administration_entity=self.entity,
                academic_year=ac_year,
            )

        result = shorten.start(self.education_group_year.education_group, self.current_academic_year.year)

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 10)
        # Ensure that the order is by academic_year.year
        for idx, ac_year in enumerate(self.generated_ac_years.academic_years):
            self.assertEqual(result[idx].academic_year, ac_year)

        # Ensure that data doesn't exist anymore
        self.assertFalse(EducationGroupYear.objects.filter(
            education_group=self.education_group_year.education_group,
            academic_year__year__gt=self.current_academic_year.year
        ).count())
