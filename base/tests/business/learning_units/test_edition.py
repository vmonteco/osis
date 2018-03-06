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
import random

from django.test import TestCase

from base.business.learning_unit_year_with_context import ENTITY_TYPES_VOLUME
from base.business.learning_units.edition import update_or_create_entity_container_year_with_components
from base.models.entity_component_year import EntityComponentYear
from base.models.entity_container_year import EntityContainerYear
from base.models.enums import entity_container_year_link_type
from base.tests.factories.entity import EntityFactory
from base.tests.factories.learning_component_year import LearningComponentYearFactory
from base.tests.factories.learning_container_year import LearningContainerYearFactory
from base.tests.factories.academic_year import create_current_academic_year


class LearningUnitEditionTestCase(TestCase):
    def setUp(self):
        self.academic_year = create_current_academic_year()

    def test_update_or_create_entity_container_year_with_components_type_requirement(self):
        """In this test, we ensure that when we create an entity_container type requirement,
           we have an entity_component created"""
        an_entity = EntityFactory()
        a_learning_container_year = LearningContainerYearFactory(academic_year=self.academic_year)
        LearningComponentYearFactory(acronym="CM", learning_container_year=a_learning_container_year)
        LearningComponentYearFactory(acronym="TP", learning_container_year=a_learning_container_year)
        link_type = random.choice(ENTITY_TYPES_VOLUME)

        update_or_create_entity_container_year_with_components(an_entity, a_learning_container_year, link_type)
        self.assertEqual(EntityContainerYear.objects.all().count(), 1)
        self.assertEqual(EntityComponentYear.objects.all().count(), 2)

    def test_update_or_create_entity_container_year_with_components_type_allocation(self):
        """In this test, we ensure that when we create an entity_container type allocation,
           we have NO entity_component created"""
        an_entity = EntityFactory()
        a_learning_container_year = LearningContainerYearFactory(academic_year=self.academic_year)
        LearningComponentYearFactory(acronym="CM", learning_container_year=a_learning_container_year)
        LearningComponentYearFactory(acronym="TP", learning_container_year=a_learning_container_year)
        link_type = entity_container_year_link_type.ALLOCATION_ENTITY

        update_or_create_entity_container_year_with_components(an_entity, a_learning_container_year, link_type)
        self.assertEqual(EntityContainerYear.objects.all().count(), 1)
        self.assertEqual(EntityComponentYear.objects.all().count(), 0)
