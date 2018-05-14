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
from django.contrib.auth.models import Permission
from django.test import TestCase

from base.forms.learning_unit.learning_unit_create import EntityContainerBaseForm
from base.models.entity import Entity
from base.models.enums import organization_type, entity_container_year_link_type, learning_unit_year_subtypes, \
    entity_type, learning_container_year_types
from base.models.enums.entity_container_year_link_type import REQUIREMENT_ENTITY, ALLOCATION_ENTITY, \
    ADDITIONAL_REQUIREMENT_ENTITY_1, ADDITIONAL_REQUIREMENT_ENTITY_2
from base.tests.factories.academic_year import create_current_academic_year
from base.tests.factories.campus import CampusFactory
from base.tests.factories.entity import EntityFactory
from base.tests.factories.entity_container_year import EntityContainerYearFactory
from base.tests.factories.entity_version import EntityVersionFactory
from base.tests.factories.learning_container_year import LearningContainerYearFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFakerFactory
from base.tests.factories.organization import OrganizationFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.person_entity import PersonEntityFactory


class TestEntityContainerYearForm(TestCase):
    def setUp(self):
        self.person = PersonFactory()
        self.permission = Permission.objects.get(codename="can_propose_learningunit")
        self.person.user.user_permissions.add(self.permission)

        self.permission_2 = Permission.objects.get(codename="can_access_learningunit")
        self.person.user.user_permissions.add(self.permission_2)
        an_organization = OrganizationFactory(type=organization_type.MAIN)
        current_academic_year = create_current_academic_year()
        learning_container_year = LearningContainerYearFactory(
            acronym="LOSIS1212",
            academic_year=current_academic_year,
            container_type=learning_container_year_types.COURSE,
            campus=CampusFactory(organization=an_organization, is_administration=True)
        )
        self.learning_unit_year = LearningUnitYearFakerFactory(acronym=learning_container_year.acronym,
                                                               subtype=learning_unit_year_subtypes.FULL,
                                                               academic_year=current_academic_year,
                                                               learning_container_year=learning_container_year,
                                                               quadrimester=None,
                                                               specific_title_english="title english")

        self.learning_container_year = self.learning_unit_year.learning_container_year
        an_entity = EntityFactory(organization=an_organization)
        self.entity_version = EntityVersionFactory(entity=an_entity, entity_type=entity_type.SCHOOL,
                                                   start_date=current_academic_year.start_date,
                                                   end_date=current_academic_year.end_date)
        self.requirement_entity = EntityContainerYearFactory(
            learning_container_year=self.learning_container_year,
            entity=self.entity_version.entity,
            type=entity_container_year_link_type.REQUIREMENT_ENTITY
        )
        self.allocation_entity = EntityContainerYearFactory(
            learning_container_year=self.learning_container_year,
            entity=self.entity_version.entity,
            type=entity_container_year_link_type.ALLOCATION_ENTITY
        )
        self.additional_requirement_entity_1 = EntityContainerYearFactory(
            learning_container_year=self.learning_container_year,
            entity=self.entity_version.entity,
            type=entity_container_year_link_type.ADDITIONAL_REQUIREMENT_ENTITY_1
        )
        self.additional_requirement_entity_2 = EntityContainerYearFactory(
            learning_container_year=self.learning_container_year,
            entity=self.entity_version.entity,
            type=entity_container_year_link_type.ADDITIONAL_REQUIREMENT_ENTITY_2
        )
        PersonEntityFactory(person=self.person, entity=self.entity_version.entity)



    def test_init(self):
        form = EntityContainerBaseForm(learning_container_year=self.learning_container_year, person=self.person)
        self.assertEqual(form.forms[0].instance.pk, self.requirement_entity.pk)
        self.assertEqual(form.forms[1].instance.pk, self.allocation_entity.pk)
        self.assertEqual(form.forms[2].instance.pk, self.additional_requirement_entity_1.pk)
        self.assertEqual(form.forms[3].instance.pk, self.additional_requirement_entity_2.pk)

    def test_save(self):

        data = {
            'requirement_entity-entity': self.entity_version.id,
            'allocation_entity-entity': self.entity_version.id,
            'additional_requirement_entity_1-entity': ''
        }

        form = EntityContainerBaseForm(data=data,
                                       learning_container_year=self.learning_container_year, person=self.person)

        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(len(form.save()), 4)

        self.assertEqual(
            Entity.objects.filter(entitycontaineryear__learning_container_year=self.learning_container_year,
                                  entitycontaineryear__type=REQUIREMENT_ENTITY).get(),
            self.entity_version.entity
        )
        self.assertEqual(
            Entity.objects.filter(entitycontaineryear__learning_container_year=self.learning_container_year,
                                  entitycontaineryear__type=ALLOCATION_ENTITY).get(),
            self.entity_version.entity
        )

    def test_save_delete_additional_instances(self):
        self.assertTrue(
            Entity.objects.filter(entitycontaineryear__learning_container_year=self.learning_container_year,
                                  entitycontaineryear__type=ADDITIONAL_REQUIREMENT_ENTITY_1).exists()
        )
        self.assertTrue(
            Entity.objects.filter(entitycontaineryear__learning_container_year=self.learning_container_year,
                                  entitycontaineryear__type=ADDITIONAL_REQUIREMENT_ENTITY_2).exists()
        )

        data = {
            'requirement_entity-entity': self.entity_version.id,
            'allocation_entity-entity': self.entity_version.id,
            'additional_requirement_entity_1-entity': ''
        }

        form = EntityContainerBaseForm(data=data,
                                       learning_container_year=self.learning_container_year, person=self.person)

        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(len(form.save()), 4)

        self.assertFalse(
            Entity.objects.filter(entitycontaineryear__learning_container_year=self.learning_container_year,
                                  entitycontaineryear__type=ADDITIONAL_REQUIREMENT_ENTITY_1).exists()
        )
        self.assertFalse(
            Entity.objects.filter(entitycontaineryear__learning_container_year=self.learning_container_year,
                                  entitycontaineryear__type=ADDITIONAL_REQUIREMENT_ENTITY_2).exists()
        )