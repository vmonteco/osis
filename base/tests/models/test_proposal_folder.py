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
from django.db.utils import IntegrityError
from base.tests.factories.proposal_folder import ProposalFolderFactory
from base.tests.factories.entity import EntityFactory
from base.tests.factories.entity_version import EntityVersionFactory
from base.models import proposal_folder, proposal_learning_unit


class TestSearch(TestCase):
    def setUp(self):
        self.entity_1 = EntityFactory()
        self.entity_version_1 = EntityVersionFactory(entity=self.entity_1)
        self.entity_2 = EntityFactory()
        self.entity_version_2 = EntityVersionFactory(entity=self.entity_2)
        self.proposal_folder = ProposalFolderFactory(entity=self.entity_1)

    def test_unique_together(self):
        with self.assertRaises(IntegrityError):
            proposal_folder.ProposalFolder.objects.create(entity=self.proposal_folder.entity,
                                                          folder_id=self.proposal_folder.folder_id)

    def test_find_by_entity_and_folder_id(self):
        ProposalFolderFactory()
        a_proposal_folder = proposal_folder.find_by_entity_and_folder_id(self.proposal_folder.entity,
                                                                         self.proposal_folder.folder_id)

        self.assertEqual(a_proposal_folder, self.proposal_folder)

    def test_find_distinct_folder_entities(self):
        ProposalFolderFactory(entity=self.entity_2)

        entities_result = proposal_folder.find_distinct_folder_entities()
        self.assertEqual(entities_result.count(), 2)
        self.assertCountEqual(entities_result, [self.entity_1, self.entity_2])
