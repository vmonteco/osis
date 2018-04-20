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
import datetime
from decimal import Decimal
from unittest import skip

from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase

from base.forms.learning_unit_proposal import ProposalBaseForm
from base.models import proposal_learning_unit, entity_container_year
from base.models.entity_container_year import EntityContainerYear
from base.models.enums import organization_type, proposal_type, proposal_state, entity_type, \
    learning_container_year_types, learning_unit_year_quadrimesters, entity_container_year_link_type, \
    learning_unit_periodicity, internship_subtypes, learning_unit_year_subtypes
from base.models.person import FACULTY_MANAGER_GROUP, CENTRAL_MANAGER_GROUP
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
from reference.tests.factories.language import LanguageFactory

PROPOSAL_TYPE = proposal_type.ProposalType.TRANSFORMATION_AND_MODIFICATION.name
PROPOSAL_STATE = proposal_state.ProposalState.FACULTY.name


class TestSave(TestCase):
    def setUp(self):
        self.person = PersonFactory()
        an_organization = OrganizationFactory(type=organization_type.MAIN)
        current_academic_year = create_current_academic_year()
        learning_container_year = LearningContainerYearFactory(
            academic_year=current_academic_year,
            container_type=learning_container_year_types.COURSE,
            campus=CampusFactory(organization=an_organization, is_administration=True)
        )
        self.learning_unit_year = LearningUnitYearFakerFactory(credits=5,
                                                               subtype=learning_unit_year_subtypes.FULL,
                                                               academic_year=current_academic_year,
                                                               learning_container_year=learning_container_year)

        self.entity_container_year = EntityContainerYearFactory(
            learning_container_year=self.learning_unit_year.learning_container_year,
            type=entity_container_year_link_type.REQUIREMENT_ENTITY
        )

        today = datetime.date.today()
        an_entity = EntityFactory(organization=an_organization)
        self.entity_version = EntityVersionFactory(entity=an_entity, entity_type=entity_type.SCHOOL, start_date=today,
                                                   end_date=today.replace(year=today.year + 1))
        PersonEntityFactory(person=self.person, entity=an_entity)
        self.language = LanguageFactory(code="EN")
        self.campus = CampusFactory(name="OSIS Campus", organization=OrganizationFactory(type=organization_type.MAIN),
                                    is_administration=True)

        self.form_data = {
            "academic_year": self.learning_unit_year.academic_year.id,
            "acronym_0": "L",
            "acronym_1": "OSIS1245",
            "common_title": "New common title",
            "common_title_english": "New common title english",
            "specific_title": "New title",
            "specific_title_english": "New title english",
            "container_type": self.learning_unit_year.learning_container_year.container_type,
            "internship_subtype": "",
            "credits": "4",
            "periodicity": learning_unit_periodicity.BIENNIAL_ODD,
            "status": False,
            "language": self.language.pk,
            "quadrimester": learning_unit_year_quadrimesters.Q1,
            "campus": self.campus.id,
            "entity": self.entity_version.id,
            "folder_id": "1",
            "state": proposal_state.ProposalState.CENTRAL.name,
            'entitycontaineryear_set-0-entity': self.entity_version.id,
            'entitycontaineryear_set-1-entity': self.entity_version.id,
            'entitycontaineryear_set-2-entity': self.entity_version.id,
            'entitycontaineryear_set-3-entity': self.entity_version.id,
            'entitycontaineryear_set-INITIAL_FORMS': '0',
            'entitycontaineryear_set-MAX_NUM_FORMS': '4',
            'entitycontaineryear_set-MIN_NUM_FORMS': '3',
            'entitycontaineryear_set-TOTAL_FORMS': '4',
        }

    def test_learning_unit_proposal_form_get_as_faculty_manager(self):
        self.person.user.groups.add(Group.objects.get(name=FACULTY_MANAGER_GROUP))
        form = ProposalBaseForm(self.form_data, self.person, self.learning_unit_year)
        self.assertTrue(form.fields['state'].disabled)

    def test_learning_unit_proposal_form_get_as_central_manager(self):
        self.person.user.groups.add(Group.objects.get(name=CENTRAL_MANAGER_GROUP))
        form = ProposalBaseForm(self.form_data, self.person, self.learning_unit_year)
        self.assertFalse(form.fields['state'].disabled)

    def test_learning_unit_year_update(self):
        form = ProposalBaseForm(self.form_data, self.person, self.learning_unit_year)
        self.assertTrue(form.is_valid())
        form.save()
        self.learning_unit_year.refresh_from_db()
        self._assert_acronym_has_changed_in_proposal()
        self._assert_common_titles_stored_in_container()
        self.assertFalse(self.learning_unit_year.status)
        self.assertEqual(self.learning_unit_year.credits, Decimal(self.form_data['credits']))
        self.assertEqual(self.learning_unit_year.quadrimester, self.form_data['quadrimester'])
        self.assertEqual(self.learning_unit_year.specific_title, self.form_data["specific_title"])
        self.assertEqual(self.learning_unit_year.specific_title_english, self.form_data["specific_title_english"])

    def _assert_acronym_has_changed_in_proposal(self):
        self.assertEqual(self.learning_unit_year.acronym,
                         "{}{}".format(self.form_data['acronym_0'], self.form_data['acronym_1']))

    def _assert_common_titles_stored_in_container(self):
        self.assertNotEqual(self.learning_unit_year.specific_title, self.form_data['common_title'])
        self.assertNotEqual(self.learning_unit_year.specific_title_english, self.form_data['common_title_english'])
        self.assertEqual(self.learning_unit_year.learning_container_year.common_title, self.form_data['common_title'])
        self.assertEqual(self.learning_unit_year.learning_container_year.common_title_english,
                         self.form_data['common_title_english'])

    def test_learning_container_update(self):
        form = ProposalBaseForm(self.form_data, self.person, self.learning_unit_year)
        self.assertTrue(form.is_valid())
        form.save()

        self.learning_unit_year.refresh_from_db()
        learning_container_year = self.learning_unit_year.learning_container_year

        self.assertEqual(self.learning_unit_year.acronym, self.form_data['acronym_0'] + self.form_data['acronym_1'])
        self.assertEqual(learning_container_year.common_title, self.form_data['common_title'])
        self.assertEqual(learning_container_year.common_title_english, self.form_data['common_title_english'])
        self.assertEqual(learning_container_year.language, self.language)
        self.assertEqual(learning_container_year.campus, self.campus)

    def test_requirement_entity(self):
        form = ProposalBaseForm(self.form_data, self.person, self.learning_unit_year)
        self.assertTrue(form.is_valid())
        form.save()

        self.entity_container_year.refresh_from_db()
        self.assertEqual(self.entity_container_year.entity, self.entity_version.entity)

    def test_with_all_entities_set(self):
        today = datetime.date.today()
        entity_1 = EntityFactory(organization=OrganizationFactory(type=organization_type.MAIN))
        additional_entity_version_1 = EntityVersionFactory(entity_type=entity_type.SCHOOL, start_date=today,
                                                           end_date=today.replace(year=today.year + 1),
                                                           entity=entity_1)
        entity_2 = EntityFactory(organization=OrganizationFactory(type=organization_type.MAIN))
        additional_entity_version_2 = EntityVersionFactory(entity_type=entity_type.SCHOOL, start_date=today,
                                                           end_date=today.replace(year=today.year + 1),
                                                           entity=entity_2)
        self.form_data["entitycontaineryear_set-1-entity"] = self.entity_version.id
        self.form_data["entitycontaineryear_set-2-entity"] = additional_entity_version_1.id
        self.form_data["entitycontaineryear_set-3-entity"] = additional_entity_version_2.id

        form = ProposalBaseForm(self.form_data, self.person, self.learning_unit_year)
        form.is_valid()
        form.save()

        entities_by_type = \
            entity_container_year.find_entities_grouped_by_linktype(self.learning_unit_year.learning_container_year)

        expected_entities = {
            entity_container_year_link_type.REQUIREMENT_ENTITY: self.entity_version.entity,
            entity_container_year_link_type.ALLOCATION_ENTITY: self.entity_version.entity,
            entity_container_year_link_type.ADDITIONAL_REQUIREMENT_ENTITY_1: additional_entity_version_1.entity,
            entity_container_year_link_type.ADDITIONAL_REQUIREMENT_ENTITY_2: additional_entity_version_2.entity
        }
        self.maxDiff = None
        self.assertDictEqual(entities_by_type, expected_entities)

    def test_modify_learning_container_subtype(self):
        self.form_data["container_type"] = learning_container_year_types.INTERNSHIP
        self.form_data["internship_subtype"] = internship_subtypes.TEACHING_INTERNSHIP

        form = ProposalBaseForm(self.form_data, self.person, self.learning_unit_year)
        self.assertTrue(form.is_valid(), form.errors)
        form.save()

        self.learning_unit_year.refresh_from_db()

        self.assertEqual(self.learning_unit_year.learning_container_year.container_type,
                         learning_container_year_types.INTERNSHIP)
        self.assertEqual(self.learning_unit_year.internship_subtype, internship_subtypes.TEACHING_INTERNSHIP)

    def test_creation_proposal_learning_unit(self):
        initial_data_expected = {
            "learning_container_year": {
                "id": self.learning_unit_year.learning_container_year.id,
                "acronym": self.learning_unit_year.acronym,
                "common_title": self.learning_unit_year.learning_container_year.common_title,
                "common_title_english": self.learning_unit_year.learning_container_year.common_title_english,
                "container_type": self.learning_unit_year.learning_container_year.container_type,
                "campus": self.learning_unit_year.learning_container_year.campus.id,
                "language": self.learning_unit_year.learning_container_year.language.pk,
                "in_charge": self.learning_unit_year.learning_container_year.in_charge
            },
            "learning_unit_year": {
                "id": self.learning_unit_year.id,
                "acronym": self.learning_unit_year.acronym,
                "specific_title": self.learning_unit_year.specific_title,
                "specific_title_english": self.learning_unit_year.specific_title_english,
                "internship_subtype": self.learning_unit_year.internship_subtype,
                "credits": self.learning_unit_year.credits,
                "status": self.learning_unit_year.status
            },
            "learning_unit": {
                "id": self.learning_unit_year.learning_unit.id,
                "periodicity": self.learning_unit_year.learning_unit.periodicity,
                'end_year': self.learning_unit_year.learning_unit.end_year
            },
            "entities": {
                entity_container_year_link_type.REQUIREMENT_ENTITY: self.entity_container_year.entity.id,
                entity_container_year_link_type.ALLOCATION_ENTITY: None,
                entity_container_year_link_type.ADDITIONAL_REQUIREMENT_ENTITY_1: "-",
                entity_container_year_link_type.ADDITIONAL_REQUIREMENT_ENTITY_2: "-"
            }
        }

        form = ProposalBaseForm(self.form_data, self.person, self.learning_unit_year)
        self.assertTrue(form.is_valid())
        form.save()

        a_proposal_learning_unt = proposal_learning_unit.find_by_learning_unit_year(self.learning_unit_year)

        self.assertEqual(a_proposal_learning_unt.type, PROPOSAL_TYPE)
        self.assertEqual(a_proposal_learning_unt.state, PROPOSAL_STATE)
        self.assertEqual(a_proposal_learning_unt.author, self.person)

        self.assertDictEqual(a_proposal_learning_unt.initial_data, initial_data_expected)

    def test_when_setting_additional_entity_to_none(self):
        self.form_data['entitycontaineryear_set-2-entity'] = None
        form = ProposalBaseForm(self.form_data, self.person, self.learning_unit_year)
        self.assertTrue(form.is_valid())
        form.save()

        with self.assertRaises(ObjectDoesNotExist):
            EntityContainerYear.objects.get(learning_container_year=self.learning_unit_year.learning_container_year,
                                            type=entity_container_year_link_type.ADDITIONAL_REQUIREMENT_ENTITY_1)
