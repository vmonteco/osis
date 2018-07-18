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

from attribution.business import summary_responsible
from attribution.tests.factories.attribution import AttributionFactory
from base.models.enums import entity_container_year_link_type
from base.models.enums import entity_type
from base.tests.factories.academic_year import create_current_academic_year, AcademicYearFactory
from base.tests.factories.entity_container_year import EntityContainerYearFactory
from base.tests.factories.entity_manager import EntityManagerFactory
from base.tests.factories.entity_version import EntityVersionFactory
from base.tests.factories.person import PersonFactory


class TestSearchAttributions(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create entity version and entity manager
        cls.entity_version = EntityVersionFactory(entity_type=entity_type.SECTOR)
        cls.entity_manager_person = PersonFactory()
        EntityManagerFactory(entity=cls.entity_version.entity, person=cls.entity_manager_person)

        cls.current_academic_year = create_current_academic_year()
        # Create multiple attribution
        for nb in range(0,10):
            attribution = AttributionFactory(
                learning_unit_year__acronym='LBIR120{}'.format(nb),
                learning_unit_year__academic_year=cls.current_academic_year,
                learning_unit_year__learning_container_year__academic_year=cls.current_academic_year,
            )
            # Link course to entity
            EntityContainerYearFactory(
                learning_container_year=attribution.learning_unit_year.learning_container_year,
                entity=cls.entity_version.entity,
                type=entity_container_year_link_type.REQUIREMENT_ENTITY,
            )

    def test_search_attributions_case_academic_year_without_any_attribution(self):
        new_academic_year = AcademicYearFactory(year=self.current_academic_year.year + 1)
        result = summary_responsible.search_attributions(new_academic_year)
        self.assertIsInstance(result, list)
        self.assertFalse(result)

    def test_search_attributions_case_academic_year_with_attributions_no_filter(self):
        result = summary_responsible.search_attributions(self.current_academic_year)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 10)

    def test_search_attributions_case_academic_year_with_attributions_with_filter(self):
        result = summary_responsible.search_attributions(
            self.current_academic_year,
            course_code='LBIR1204'
        )
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
