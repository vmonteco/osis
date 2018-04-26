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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django.test import TestCase
from base.tests.factories.entity import EntityFactory
from base.tests.factories.entity_version import EntityVersionFactory

from base.business.entity import get_entity_calendar

from base.tests.factories.entity_calendar import EntityCalendarFactory
from base.tests.factories.academic_calendar import AcademicCalendarFactory
from base.models.enums import academic_calendar_type
from base.tests.factories.academic_year import create_current_academic_year
from base.business.learning_unit import get_list_entity_learning_unit_yr
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.learning_container_year import LearningContainerYearFactory
from reference.tests.factories.country import CountryFactory
from base.models.enums import learning_container_year_types
from base.tests.factories.entity_container_year import EntityContainerYearFactory
from base.tests.factories.entity_version import EntityVersionFactory
from base.models.enums import entity_container_year_link_type
from base.models.enums import learning_unit_year_subtypes


class LearningUnitTestCase(TestCase):
    def setUp(self):
        self.current_academic_year = create_current_academic_year()
        country = CountryFactory()
        ssh_entity = EntityFactory(country=country)
        ssh_entity_v = EntityVersionFactory(acronym="SSH", end_date=None, entity=ssh_entity)

        agro_entity = EntityFactory(country=country)

        self.agro_entity_v = EntityVersionFactory(entity=agro_entity, parent=ssh_entity_v.entity, acronym="AGRO",
                                                  end_date=None)

        l_container_yr = LearningContainerYearFactory(acronym="LBIR1100", academic_year=self.current_academic_year,
                                                      container_type=learning_container_year_types.COURSE)
        EntityContainerYearFactory(learning_container_year=l_container_yr, entity=self.agro_entity_v.entity,
                                   type=entity_container_year_link_type.REQUIREMENT_ENTITY)
        self.learning_unit_1 = LearningUnitYearFactory(acronym="LBIR1100", learning_container_year=l_container_yr,
                                                       academic_year=self.current_academic_year,
                                                       subtype=learning_unit_year_subtypes.FULL)
        self.learning_unit_2 = LearningUnitYearFactory(acronym="LBIR1100B", learning_container_year=l_container_yr,
                                                       academic_year=self.current_academic_year,
                                                       subtype=learning_unit_year_subtypes.PARTIM)
        self.learning_unit_3 = LearningUnitYearFactory(acronym="LBIR1100A", learning_container_year=l_container_yr,
                                                       academic_year=self.current_academic_year,
                                                       subtype=learning_unit_year_subtypes.PARTIM)
        self.learning_unit_4 = LearningUnitYearFactory(acronym="LBIR1100C", learning_container_year=l_container_yr,
                                                       academic_year=self.current_academic_year,
                                                       subtype=learning_unit_year_subtypes.PARTIM,
                                                       status=False)

    def test_get_list_entity_learning_unit_yr(self):
        self.assertCountEqual(get_list_entity_learning_unit_yr(self.agro_entity_v, self.current_academic_year),
                              [self.learning_unit_1,
                               self.learning_unit_2, self.learning_unit_3])

    def test_get_list_entity_learning_unit_yr_check_order(self):
        results = get_list_entity_learning_unit_yr(self.agro_entity_v, self.current_academic_year)
        self.assertEqual(results[0], self.learning_unit_1)
        self.assertEqual(results[1], self.learning_unit_3)
        self.assertEqual(results[2], self.learning_unit_2)
