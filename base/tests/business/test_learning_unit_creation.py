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
from decimal import Decimal
from unittest import mock

from django.test import TestCase

import base.models.academic_year
from base.business.learning_units.simple import creation
from base import models as mdl_base
from base.models.enums import entity_container_year_link_type
from base.models.enums import learning_component_year_type
from base.models.enums import learning_container_year_types
from base.tests.factories.academic_year import create_current_academic_year
from base.tests.factories.entity_container_year import EntityContainerYearFactory
from base.tests.factories.entity_version import EntityVersionFactory
from base.tests.factories.learning_container import LearningContainerFactory
from base.tests.factories.learning_container_year import LearningContainerYearFactory
from base.tests.factories.learning_unit import LearningUnitFactory


class LearningUnitCreationTest(TestCase):

    def setUp(self):
        self.current_academic_year = create_current_academic_year()

    def test_compute_max_academic_year_adjournment(self):
        self.assertEqual(base.models.academic_year.compute_max_academic_year_adjournment(),
                         self.current_academic_year.year + base.models.academic_year.LEARNING_UNIT_CREATION_SPAN_YEARS)

    def test_create_learning_unit_year(self):
        data_dict = self.get_data_dict(learning_container_year_types.OTHER_COLLECTIVE)
        data = data_dict.get('data')
        new_learning_unit_yr = creation.create_learning_unit_year(data_dict)
        self.assertEqual(new_learning_unit_yr.academic_year, data_dict.get('academic_year'))

        self.assertEqual(new_learning_unit_yr.learning_unit, data_dict.get('new_learning_unit'))
        self.assertEqual(new_learning_unit_yr.learning_container_year, data_dict.get('new_learning_container_year'))
        self.assertEqual(new_learning_unit_yr.acronym, data.get('acronym').upper())
        self.assertEqual(new_learning_unit_yr.specific_title, data.get('specific_title'))
        self.assertEqual(new_learning_unit_yr.specific_title_english, data.get('specific_title_english'))
        self.assertEqual(new_learning_unit_yr.subtype, data.get('subtype'))
        self.assertEqual(new_learning_unit_yr.credits, data.get('credits'))
        self.assertEqual(new_learning_unit_yr.internship_subtype, data.get('internship_subtype'))
        self.assertEqual(new_learning_unit_yr.status, data.get('status'))
        self.assertEqual(new_learning_unit_yr.session, data.get('session'))
        self.assertEqual(new_learning_unit_yr.quadrimester, data.get('quadrimester'))

    def test_create_learning_component_year(self):
        learning_container = LearningContainerFactory()
        learning_container_yr = LearningContainerYearFactory(academic_year=self.current_academic_year,
                                                             learning_container=learning_container)

        new_learning_component_yr = creation.create_learning_component_year(learning_container_yr,
                                                                            creation.DEFAULT_ACRONYM_LECTURING_COMPONENT,
                                                                            learning_component_year_type.LECTURING)
        self.assertEqual(new_learning_component_yr.learning_container_year, learning_container_yr)
        self.assertEqual(new_learning_component_yr.acronym,
                         creation.DEFAULT_ACRONYM_LECTURING_COMPONENT)
        self.assertEqual(new_learning_component_yr.type, learning_component_year_type.LECTURING)

    def test_create_with_lecturing_and_practical_components(self):
        data_dict = self.get_data_dict(learning_container_year_types.OTHER_COLLECTIVE)
        creation.create_with_lecturing_and_practical_components(data_dict)

        self.assertEqual(mdl_base.learning_component_year.LearningComponentYear.objects.all().count(), 2)
        self.assertEqual(mdl_base.learning_component_year.LearningComponentYear.objects
                         .filter(type=learning_component_year_type.LECTURING).count(), 1)
        self.assertEqual(mdl_base.learning_component_year.LearningComponentYear.objects
                         .filter(type=learning_component_year_type.PRACTICAL_EXERCISES).count(), 1)

        self.assertEqual(mdl_base.entity_component_year.EntityComponentYear.objects.all().count(), 2)

        self.assertEqual(mdl_base.learning_unit_year.LearningUnitYear.objects.all().count(), 1)

        self.assertEqual(mdl_base.learning_unit_component.LearningUnitComponent.objects.all().count(), 2)
        self.assertEqual(mdl_base.learning_unit_component.LearningUnitComponent.objects
                         .filter(type=learning_component_year_type.LECTURING).count(), 1)
        self.assertEqual(mdl_base.learning_unit_component.LearningUnitComponent.objects
                         .filter(type=learning_component_year_type.PRACTICAL_EXERCISES).count(), 1)

    def test_create_with_untyped_component(self):
        data_dict = self.get_data_dict(learning_container_year_types.OTHER_COLLECTIVE)
        creation.create_with_untyped_component(data_dict)
        self.assertEqual(mdl_base.learning_component_year.LearningComponentYear.objects.all().count(), 1)
        self.assertEqual(mdl_base.learning_component_year.LearningComponentYear.objects
                         .filter(acronym=creation.UNTYPED_ACRONYM).count(), 1)
        self.assertEqual(mdl_base.learning_component_year.LearningComponentYear.objects
                         .filter(type__isnull=True).count(), 1)
        self.assertEqual(mdl_base.entity_component_year.EntityComponentYear.objects.all().count(), 1)
        self.assertEqual(mdl_base.learning_unit_year.LearningUnitYear.objects.all().count(), 1)
        self.assertEqual(mdl_base.learning_unit_component.LearningUnitComponent.objects.all().count(), 1)

    def test_create_with_untyped_component_multiple_requirements_entities(self):
        data_dict = self.get_data_dict(learning_container_year_types.OTHER_COLLECTIVE)
        data_dict['requirement_entity_containers'].append(
            EntityContainerYearFactory(learning_container_year=data_dict['new_learning_container_year'],
                                       type=entity_container_year_link_type.ADDITIONAL_REQUIREMENT_ENTITY_1))
        creation.create_with_untyped_component(data_dict)
        self.assertEqual(mdl_base.learning_component_year.LearningComponentYear.objects.all().count(), 1)
        self.assertEqual(mdl_base.learning_component_year.LearningComponentYear.objects
                         .filter(acronym=creation.UNTYPED_ACRONYM).count(), 1)
        self.assertEqual(mdl_base.learning_component_year.LearningComponentYear.objects
                         .filter(type__isnull=True).count(), 1)
        # We should have two entity component year [Requirement + 1 additional]
        self.assertEqual(mdl_base.entity_component_year.EntityComponentYear.objects.all().count(), 2)
        self.assertEqual(mdl_base.learning_unit_year.LearningUnitYear.objects.all().count(), 1)
        self.assertEqual(mdl_base.learning_unit_component.LearningUnitComponent.objects.all().count(), 1)

    @mock.patch("base.business.learning_units.simple.creation.create_with_lecturing_and_practical_components")
    def test_create_learning_unit_content_create_with_lecturing_and_practical_components(self, mock):
        container_type_with_default_component = [learning_container_year_types.COURSE,
                                                 learning_container_year_types.MASTER_THESIS,
                                                 learning_container_year_types.OTHER_COLLECTIVE,
                                                 learning_container_year_types.INTERNSHIP]
        for container_type in container_type_with_default_component:
            data_dict = self.get_data_dict(container_type)
            creation.create_learning_unit_content(data_dict)
            self.assertTrue(mock.called)

    @mock.patch("base.business.learning_units.simple.creation.create_with_untyped_component")
    def test_create_learning_unit_content_create_with_untyped_component(self, mock):
        container_type_without_default_component = [learning_container_year_types.DISSERTATION,
                                                    learning_container_year_types.OTHER_INDIVIDUAL,
                                                    learning_container_year_types.EXTERNAL]
        for container_type in container_type_without_default_component:
            data_dict = self.get_data_dict(container_type)
            creation.create_learning_unit_content(data_dict)
            self.assertTrue(mock.called)

    def get_data_dict(self, container_type):
        learning_container = LearningContainerFactory()
        learning_container_yr = LearningContainerYearFactory(academic_year=self.current_academic_year,
                                                             learning_container=learning_container)
        entity_version = EntityVersionFactory()
        a_learning_unit = LearningUnitFactory()
        requirement_entity_container_yr = EntityContainerYearFactory(
            learning_container_year=learning_container_yr,
            type=entity_container_year_link_type.REQUIREMENT_ENTITY
        )

        return {
            'new_learning_container_year': learning_container_yr,
            'data': {
                'quadrimester': '',
                'acronym': 'LTATO1200',
                'subtype': 'FULL',
                'allocation_entity': entity_version,
                'additional_requirement_entity_2': None,
                'status': True,
                'academic_year': self.current_academic_year,
                'requirement_entity': entity_version,
                'credits': Decimal('15'),
                'container_type': container_type,
                'session': '',
                'additional_requirement_entity_1': None,
                'specific_title': "Title"
            },
            'new_learning_unit': a_learning_unit,
            'requirement_entity_containers': [requirement_entity_container_yr],
            'status': True,
            'academic_year': self.current_academic_year
        }
