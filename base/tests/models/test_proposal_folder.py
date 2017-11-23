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
from django.test import TestCase

from base.tests.factories.proposal_folder import ProposalFolderFactory
from base.models import proposal_folder


class TestSearch(TestCase):
    def setUp(self):
        self.proposal_folder = ProposalFolderFactory()

    def test_find_by_entiy_and_folder_id(self):
        ProposalFolderFactory()
        a_proposal_folder = proposal_folder.find_by_entity_and_folder_id(self.proposal_folder.entity,
                                                                         self.proposal_folder.folder_id)

        self.assertEqual(a_proposal_folder, self.proposal_folder)