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
from unittest.mock import patch

from base.business.learning_unit_proposal import compute_proposal_type
from base.tests.factories.person import PersonFactory
from base.tests.factories.proposal_learning_unit import ProposalLearningUnitFactory
from base.business import learning_unit_proposal as lu_proposal_business
from base import models as mdl_base

from django.test import TestCase, SimpleTestCase

from base.models.enums import organization_type, proposal_type, entity_type, \
    learning_container_year_types, entity_container_year_link_type, \
    learning_unit_year_subtypes, proposal_state, learning_unit_periodicity
from base.tests.factories.academic_year import create_current_academic_year
from base.tests.factories.campus import CampusFactory
from base.tests.factories.entity import EntityFactory
from base.tests.factories.entity_container_year import EntityContainerYearFactory
from base.tests.factories.entity_version import EntityVersionFactory
from base.tests.factories.learning_container_year import LearningContainerYearFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFakerFactory
from base.tests.factories.organization import OrganizationFactory


class TestLearningUnitProposal(TestCase):

    def test_get_data_dict(self):
        self.assertIsNone(lu_proposal_business._get_data_dict('key1', None))
        self.assertIsNone(lu_proposal_business._get_data_dict('key1', {'key2': 'nothing serious'}))
        self.assertEqual(lu_proposal_business._get_data_dict('key1', {'key1': 'nothing serious'}), 'nothing serious')

    def test_get_data_dict(self):
        data = {'key1': 'thing', 'key2': ''}
        self.assertEqual(lu_proposal_business._get_rid_of_blank_value(data),
                         {'key1': 'thing', 'key2': None})


class TestLearningUnitProposalCancel(TestCase):
    def setUp(self):
        current_academic_year = create_current_academic_year()
        an_organization = OrganizationFactory(type=organization_type.MAIN)
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

    def test_cancel_proposal_of_type_suppression_case_success(self):
        proposal = self._create_proposal(prop_type=proposal_type.ProposalType.SUPPRESSION.name,
                                         prop_state=proposal_state.ProposalState.FACULTY.name)
        lu_proposal_business.cancel_proposal(proposal, PersonFactory(), send_mail=False)
        self.assertCountEqual(list(mdl_base.proposal_learning_unit.ProposalLearningUnit.objects
                                   .filter(learning_unit_year=self.learning_unit_year)), [])

    def test_cancel_proposal_of_type_creation_case_success(self):
        proposal = self._create_proposal(prop_type=proposal_type.ProposalType.CREATION.name,
                                         prop_state=proposal_state.ProposalState.FACULTY.name)
        lu = proposal.learning_unit_year.learning_unit
        lu_proposal_business.cancel_proposal(proposal, PersonFactory(), send_mail=False)
        self.assertCountEqual(list(mdl_base.proposal_learning_unit.ProposalLearningUnit.objects
                                   .filter(learning_unit_year=self.learning_unit_year)), [])
        self.assertCountEqual(list(mdl_base.learning_unit.LearningUnit.objects.filter(id=lu.id)),
                              [])

    @patch('base.utils.send_mail.send_mail_after_the_learning_unit_proposal_cancellation')
    def test_cancel_proposals_of_type_suppression(self, mock_send_mail):
        proposal = self._create_proposal(prop_type=proposal_type.ProposalType.SUPPRESSION.name,
                                         prop_state=proposal_state.ProposalState.FACULTY.name)
        lu_proposal_business.cancel_proposals([proposal], PersonFactory())
        self.assertCountEqual(list(mdl_base.proposal_learning_unit.ProposalLearningUnit.objects
                                   .filter(learning_unit_year=self.learning_unit_year)), [])
        self.assertTrue(mock_send_mail.called)

    @patch('base.utils.send_mail.send_mail_after_the_learning_unit_proposal_cancellation')
    def test_send_mail_after_proposal_cancellation(self, mock_send_mail):
        proposal = self._create_proposal(prop_type=proposal_type.ProposalType.SUPPRESSION.name,
                                         prop_state=proposal_state.ProposalState.FACULTY.name)
        lu_proposal_business.cancel_proposal(proposal, PersonFactory())
        self.assertTrue(mock_send_mail.called)

    def _create_proposal(self, prop_type, prop_state):
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
                "quadrimester": self.learning_unit_year.quadrimester,
                "status": self.learning_unit_year.status
            },
            "learning_unit": {
                "id": self.learning_unit_year.learning_unit.id,
                "periodicity": self.learning_unit_year.learning_unit.periodicity
            },
            "entities": {
                entity_container_year_link_type.REQUIREMENT_ENTITY: self.entity_container_year.entity.id,
                entity_container_year_link_type.ALLOCATION_ENTITY: None,
                entity_container_year_link_type.ADDITIONAL_REQUIREMENT_ENTITY_1: None,
                entity_container_year_link_type.ADDITIONAL_REQUIREMENT_ENTITY_2: None
            }
        }
        return ProposalLearningUnitFactory(learning_unit_year=self.learning_unit_year,
                                           initial_data=initial_data_expected,
                                           type=prop_type,
                                           state=prop_state)


class TestComputeProposalType(SimpleTestCase):
    def setUp(self):
        self.initial_data = {
            "academic_year": 10,
            "first_letter": "L",
            "acronym": "OSIS1245",
            "common_title": "common title",
            "common_title_english": "common title english",
            "specific_title": "itle",
            "specific_title_english": "title english",
            "container_type": learning_container_year_types.COURSE,
            "internship_subtype": "",
            "credits": "4",
            "periodicity": learning_unit_periodicity.ANNUAL,
            "status": False,
            "language": 10,
            "quadrimester": 10,
            "campus": 10,
            "requirement_entity": 10,
            "allocation_entity": 10,
            "entity": 10,
            "folder_id": "1",
            "state": proposal_state.ProposalState.CENTRAL.name,
        }

        self.new_data = self.initial_data.copy()

    def test_cannot_switch_initial_proposal_type_when_of_type_creation(self):
        creation_proposal_type = proposal_type.ProposalType.CREATION.name
        self.initial_data["type"] = creation_proposal_type

        self.assert_proposal_type(creation_proposal_type)

    def test_cannot_switch_initial_proposal_type_when_of_type_suppression(self):
        suppression_proposal_type = proposal_type.ProposalType.SUPPRESSION.name
        self.initial_data["type"] = suppression_proposal_type

        self.assert_proposal_type(suppression_proposal_type)

    def test_return_transformation_type_when_modifying_only_first_letter(self):
        self.new_data["first_letter"] = "B"

        self.assert_proposal_type(proposal_type.ProposalType.TRANSFORMATION.name)

    def test_return_transformation_type_when_modifying_only_acronym(self):
        self.new_data["acronym"] = "OSIS2569"

        self.assert_proposal_type(proposal_type.ProposalType.TRANSFORMATION.name)

    def test_return_transformation_type_when_modifying_first_letter_and_acronym(self):
        self.new_data["first_letter"] = "B"
        self.new_data["acronym"] = "OSIS2569"

        self.assert_proposal_type(proposal_type.ProposalType.TRANSFORMATION.name)

    def test_return_modification_type_when_modifying_learning_unit_fields_other_than_first_letter_and_acronym(self):
        fields_to_test = ("common_title", "common_title_english", "specific_title", "specific_title_english",
                          "container_type", "internship_subtype", "credits", "periodicity", "status", "language",
                          "quadrimester", "campus", "requirement_entity", "allocation_entity")

        for field in fields_to_test:
            if type(self.new_data[field]) == int:
                self.new_data[field] += 1
                self.assert_proposal_type(proposal_type.ProposalType.MODIFICATION.name)
                self.new_data[field] = self.initial_data[field]
            elif type(self.new_data[field]) == str:
                self.new_data[field] += "new"
                self.assert_proposal_type(proposal_type.ProposalType.MODIFICATION.name)
                self.new_data[field] = self.initial_data[field]
            elif type(self.new_data[field]) == bool:
                self.new_data[field] ^= True
                self.assert_proposal_type(proposal_type.ProposalType.MODIFICATION.name)
                self.new_data[field] = self.initial_data[field]

    def test_return_transformation_and_modification_type_when_modifying_acronym_plus_other_learning_unit_field(self):
        self.new_data["acronym"] = "OSIS2569"
        self.new_data["common_title"] =  "new common title"

        self.assert_proposal_type(proposal_type.ProposalType.TRANSFORMATION_AND_MODIFICATION.name)

    def assert_proposal_type(self, expected_proposal_type):
        actual_proposal_type = compute_proposal_type(self.initial_data, self.new_data)

        self.assertEqual(expected_proposal_type, actual_proposal_type)



