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

from copy import deepcopy
from uuid import uuid4

from django.test import TestCase

from base.business.learning_unit_year_with_context import ENTITY_TYPES_VOLUME
from base.business.learning_units.edition import update_or_create_entity_container_year_with_components, \
    _check_postponement_conflict_on_learning_unit_year, _check_postponement_conflict_on_learning_container_year, \
    _check_postponement_conflict_on_entity_container_year, check_postponement_conflict
from base.models.entity_component_year import EntityComponentYear
from base.models.entity_container_year import EntityContainerYear
from base.models.entity_version import EntityVersion
from base.models.enums import entity_container_year_link_type
from base.tests.factories.campus import CampusFactory
from base.tests.factories.entity import EntityFactory
from base.tests.factories.entity_container_year import EntityContainerYearFactory
from base.tests.factories.entity_version import EntityVersionFactory
from base.tests.factories.learning_component_year import LearningComponentYearFactory
from base.tests.factories.learning_container_year import LearningContainerYearFactory
from base.tests.factories.academic_year import create_current_academic_year, AcademicYearFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from django.utils.translation import ugettext_lazy as _

from reference.tests.factories.language import LanguageFactory


class LearningUnitEditionTestCase(TestCase):
    def setUp(self):
        self.academic_year = create_current_academic_year()
        self.next_academic_year = AcademicYearFactory(year= self.academic_year.year + 1)

        self.learning_container_year = LearningContainerYearFactory(academic_year=self.academic_year,
                                                                    common_title='common title',
                                                                    language=LanguageFactory(code='EN', name='English'),
                                                                    campus=CampusFactory(name='MIT'))
        self.learning_unit_year = LearningUnitYearFactory(academic_year=self.academic_year,
                                                          learning_container_year=self.learning_container_year,
                                                          acronym='LBIR1200',
                                                          specific_title='Chimie en laboratoire',
                                                          specific_title_english='Chimistry in laboratory')
        an_entity = EntityFactory()
        EntityVersionFactory(entity=an_entity, parent=None, end_date=None, acronym="DRT")
        self.allocation_entity = EntityContainerYearFactory(
            learning_container_year=self.learning_container_year,
            type=entity_container_year_link_type.ALLOCATION_ENTITY,
            entity=an_entity
        )
        self.requirement_entity = EntityContainerYearFactory(
            learning_container_year=self.learning_container_year,
            type=entity_container_year_link_type.REQUIREMENT_ENTITY,
            entity=an_entity
        )
        self.add_requirement_entity_1 = EntityContainerYearFactory(
            learning_container_year=self.learning_container_year,
            type=entity_container_year_link_type.ADDITIONAL_REQUIREMENT_ENTITY_1,
            entity=an_entity
        )

    def test_update_or_create_entity_container_year_with_components_type_requirement(self):
        """In this test, we ensure that when we create an entity_container type requirement,
           we have an entity_component created"""
        an_entity = EntityFactory()
        a_learning_container_year = LearningContainerYearFactory(academic_year=self.academic_year)
        LearningComponentYearFactory(acronym="CM", learning_container_year=a_learning_container_year)
        LearningComponentYearFactory(acronym="TP", learning_container_year=a_learning_container_year)
        link_type = random.choice(ENTITY_TYPES_VOLUME)

        update_or_create_entity_container_year_with_components(an_entity, a_learning_container_year, link_type)
        self.assertEqual(EntityContainerYear.objects.filter(
            learning_container_year=a_learning_container_year).count(), 1)
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
        self.assertEqual(EntityContainerYear.objects.filter(
            learning_container_year=a_learning_container_year).count(), 1)
        self.assertEqual(EntityComponentYear.objects.all().count(), 0)

    def test_check_postponement_conflict_learning_unit_year_no_differences(self):
        # Copy the same learning unit + change academic year
        another_learning_unit_year = _build_copy(self.learning_unit_year)
        another_learning_unit_year.academic_year = self.next_academic_year
        another_learning_unit_year.save()

        error_list = _check_postponement_conflict_on_learning_unit_year(self.learning_unit_year,
                                                                        another_learning_unit_year)
        self.assertIsInstance(error_list, list)
        self.assertFalse(error_list)

    def test_check_postponement_conflict_learning_unit_year_differences_found(self):
        # Copy the same learning unit + change academic year / acronym / specific_title_english
        another_learning_unit_year = _build_copy(self.learning_unit_year)
        another_learning_unit_year.academic_year = self.next_academic_year
        another_learning_unit_year.acronym = 'LBIR1000'
        another_learning_unit_year.specific_title_english = None  # Remove value
        another_learning_unit_year.save()

        error_list = _check_postponement_conflict_on_learning_unit_year(self.learning_unit_year,
                                                                        another_learning_unit_year)
        self.assertIsInstance(error_list, list)
        self.assertEqual(len(error_list), 2)
        generic_error = "The value of field '%(field)s' is different between year %(year)s - %(value)s " \
                        "and year %(next_year)s - %(next_value)s"
        # Error : Acronym diff
        error_acronym = _(generic_error) % {
            'field': _('acronym'),
            'year': self.learning_unit_year.academic_year,
            'value': getattr(self.learning_unit_year, 'acronym'),
            'next_year': another_learning_unit_year.academic_year,
            'next_value': getattr(another_learning_unit_year, 'acronym')
        }
        self.assertIn(error_acronym, error_list)
        # Error : Specific title english diff
        error_specific_title_english = _(generic_error) % {
            'field': _('specific_title_english'),
            'year': self.learning_unit_year.academic_year,
            'value': getattr(self.learning_unit_year, 'specific_title_english'),
            'next_year': another_learning_unit_year.academic_year,
            'next_value': _('no_data')
        }
        self.assertIn(error_specific_title_english, error_list)

    def test_check_postponement_conflict_learning_container_year_no_differences(self):
        # Copy the same + change academic year
        another_learning_container_year = _build_copy(self.learning_container_year)
        another_learning_container_year.academic_year = self.next_academic_year
        another_learning_container_year.save()
        # No diff found
        error_list = _check_postponement_conflict_on_learning_container_year(self.learning_container_year,
                                                                             another_learning_container_year)
        self.assertIsInstance(error_list, list)
        self.assertFalse(error_list)

    def test_check_postponement_conflict_learning_container_year_differences_found(self):
        # Copy the same container + change academic year + language + campus + common title
        another_learning_container_year = _build_copy(self.learning_container_year)
        another_learning_container_year.academic_year = self.next_academic_year
        another_learning_container_year.language = LanguageFactory(code='FR', name='French')
        another_learning_container_year.campus = CampusFactory(name='Paris')
        another_learning_container_year.common_title = 'Another common title'
        another_learning_container_year.save()

        error_list = _check_postponement_conflict_on_learning_container_year(self.learning_container_year,
                                                                             another_learning_container_year)
        self.assertIsInstance(error_list, list)
        self.assertEqual(len(error_list), 3)
        generic_error = "The value of field '%(field)s' is different between year %(year)s - %(value)s " \
                        "and year %(next_year)s - %(next_value)s"
        # Error : Language diff
        error_language = _(generic_error) % {
            'field': _('language'),
            'year': self.learning_container_year.academic_year,
            'value': getattr(self.learning_container_year, 'language'),
            'next_year': another_learning_container_year.academic_year,
            'next_value': getattr(another_learning_container_year, 'language')
        }
        self.assertIn(error_language, error_list)
        # Error : Language diff
        error_language = _(generic_error) % {
            'field': _('language'),
            'year': self.learning_container_year.academic_year,
            'value': getattr(self.learning_container_year, 'language'),
            'next_year': another_learning_container_year.academic_year,
            'next_value': getattr(another_learning_container_year, 'language')
        }
        self.assertIn(error_language, error_list)

        # Error : Campus diff
        error_language = _(generic_error) % {
            'field': _('campus'),
            'year': self.learning_container_year.academic_year,
            'value': getattr(self.learning_container_year, 'campus'),
            'next_year': another_learning_container_year.academic_year,
            'next_value': getattr(another_learning_container_year, 'campus')
        }
        self.assertIn(error_language, error_list)

        # Error : Common title diff
        error_language = _(generic_error) % {
            'field': _('common_title'),
            'year': self.learning_container_year.academic_year,
            'value': getattr(self.learning_container_year, 'common_title'),
            'next_year': another_learning_container_year.academic_year,
            'next_value': getattr(another_learning_container_year, 'common_title')
        }
        self.assertIn(error_language, error_list)

    def test_check_postponement_conflict_entity_container_year_no_difference_found(self):
        # Copy the same container + change academic year
        another_learning_container_year = _build_copy(self.learning_container_year)
        another_learning_container_year.academic_year = self.next_academic_year
        another_learning_container_year.save()

        # Copy same entity
        for entity_container_to_copy in [self.allocation_entity, self.requirement_entity,
                                         self.add_requirement_entity_1]:
            entity_copied = _build_copy(entity_container_to_copy)
            entity_copied.learning_container_year = another_learning_container_year
            entity_copied.save()

        # No diff found
        error_list = _check_postponement_conflict_on_entity_container_year(self.learning_container_year,
                                                                           another_learning_container_year)
        self.assertIsInstance(error_list, list)
        self.assertFalse(error_list)

    def test_check_postponement_conflict_entity_container_year_differences_found(self):
        # Copy the same container + change academic year
        another_learning_container_year = _build_copy(self.learning_container_year)
        another_learning_container_year.academic_year = self.next_academic_year
        another_learning_container_year.save()

        # Copy same allocation entity
        allocation_entity = _build_copy(self.allocation_entity)
        allocation_entity.learning_container_year = another_learning_container_year
        allocation_entity.save()

        # Link to another entity for requirement
        an_entity = EntityFactory()
        EntityVersionFactory(entity=an_entity, parent=None, end_date=None, acronym="AREC")
        requirement_entity = EntityContainerYearFactory(learning_container_year=another_learning_container_year,
                                                        type=entity_container_year_link_type.REQUIREMENT_ENTITY,
                                                        entity=an_entity)

        error_list = _check_postponement_conflict_on_entity_container_year(self.learning_container_year,
                                                                           another_learning_container_year)
        self.assertIsInstance(error_list, list)
        self.assertEqual(len(error_list), 2)
        generic_error = "The value of field '%(field)s' is different between year %(year)s - %(value)s " \
                        "and year %(next_year)s - %(next_value)s"
        # Error : Requirement entity diff
        error_requirement_entity = _(generic_error) % {
            'field': _(entity_container_year_link_type.REQUIREMENT_ENTITY.lower()),
            'year': self.learning_container_year.academic_year,
            'value': self.requirement_entity.entity.most_recent_acronym,
            'next_year': another_learning_container_year.academic_year,
            'next_value': requirement_entity.entity.most_recent_acronym
        }
        self.assertIn(error_requirement_entity, error_list)

        # Error : Additional requirement entity diff
        error_requirement_entity = _(generic_error) % {
            'field': _(entity_container_year_link_type.ADDITIONAL_REQUIREMENT_ENTITY_1.lower()),
            'year': self.learning_container_year.academic_year,
            'value': self.add_requirement_entity_1.entity.most_recent_acronym,
            'next_year': another_learning_container_year.academic_year,
            'next_value': _('no_data')
        }
        self.assertIn(error_requirement_entity, error_list)

    def test_check_postponement_conflict_on_all_sections(self):
        # LEARNING CONTAINER YEAR - Title modified
        another_learning_container_year = _build_copy(self.learning_container_year)
        another_learning_container_year.academic_year = self.next_academic_year
        another_learning_container_year.common_title = "Title Modified"
        another_learning_container_year.save()

        # LEARNING UNIT YEAR - Modify specific title
        another_learning_unit_year = _build_copy(self.learning_unit_year)
        another_learning_unit_year.academic_year = self.next_academic_year
        another_learning_unit_year.learning_container_year = another_learning_container_year
        another_learning_unit_year.specific_title = "Specific title modified"
        another_learning_unit_year.save()

        # ENTITY - Same allocation but NOT same requirement entity
        allocation_entity = _build_copy(self.allocation_entity)
        allocation_entity.learning_container_year = another_learning_container_year
        allocation_entity.save()
        an_entity = EntityFactory()
        EntityVersionFactory(entity=an_entity, parent=None, end_date=None, acronym="AREC")
        EntityContainerYearFactory(learning_container_year=another_learning_container_year,
                                   type=entity_container_year_link_type.REQUIREMENT_ENTITY,
                                   entity=an_entity)

        error_list = check_postponement_conflict(self.learning_unit_year)
        self.assertIsInstance(error_list, list)
        self.assertEqual(len(error_list), 4)


def _build_copy(instance):
    instance_copy = deepcopy(instance)
    instance_copy.pk = None
    instance_copy.uuid = uuid4()
    return instance_copy
