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

from base.tests.factories.person import PersonFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFakerFactory
from base.tests.factories.entity_version import EntityVersionFactory
from base.tests.factories.entity import EntityFactory
from base.tests.factories.organization import OrganizationFactory
from base.models.enums import organization_type, proposal_type, proposal_state, entity_type
from base


class TestSaveFromFormData(TestCase):
    def setUp(self):
        self.person = PersonFactory()
        an_organization = OrganizationFactory(type=organization_type.MAIN)
        self.learning_unit_year = LearningUnitYearFakerFactory(acronym="LOSIS1212")
        self.learning_unit_year.learning_container_year.campus.organization = an_organization
        self.learning_unit_year.learning_container_year.campus.is_administration = True
        self.learning_unit_year.learning_container_year.campus.save()

        today = datetime.date.today()
        an_entity = EntityFactory(organization=an_organization)
        self.entity_version = EntityVersionFactory(entity=an_entity, entity_type=entity_type.SCHOOL, start_date=today,
                                                   end_date=today.replace(year=today.year + 1))

        self.form_data = {
            "academic_year": self.learning_unit_year.academic_year.id,
            "first_letter": self.learning_unit_year.acronym[0],
            "acronym": self.learning_unit_year.acronym[1:],
            "title": self.learning_unit_year.title,
            "title_english": self.learning_unit_year.title_english,
            "learning_container_year_type": self.learning_unit_year.learning_container_year.container_type,
            "subtype": self.learning_unit_year.subtype,
            "internship_subtype": self.learning_unit_year.internship_subtype,
            "credits": self.learning_unit_year.credits,
            "periodicity": self.learning_unit_year.learning_unit.periodicity,
            "status": self.learning_unit_year.status,
            "language": self.learning_unit_year.learning_container_year.language.id,
            "quadrimester": self.learning_unit_year.quadrimester,
            "campus": self.learning_unit_year.learning_container_year.campus.id,
            "requirement_entity": self.entity_version.id,
            "type_proposal": proposal_type.ProposalType.MODIFICATION.name,
            "state_proposal": proposal_state.ProposalState.FACULTY.name,
            "person": self.person.pk,
            "folder_entity": self.entity_version.id,
            "folder_id": "1",
            "date": datetime.date.today()
        }

    def test_models_update(self):

