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
#############################################################################
from django.test import TestCase

from base.business.education_groups.learning_units.prerequisite import extract_learning_units_acronym_from_prerequisite


class TestLearningUnitsAcronymsFromPrerequisite(TestCase):
    def test_empty_prerequisite_should_return_empty_list(self):
        self.assertEqual(extract_learning_units_acronym_from_prerequisite(""),
                         [])

    def test_when_prerequisite_consits_of_one_learning_unit(self):
        self.assertEqual(extract_learning_units_acronym_from_prerequisite("LSINF1121"),
                         ["LSINF1121"])

    def test_when_prerequisites_multiple_learning_units_but_no_parentheses(self):
        self.assertEqual(extract_learning_units_acronym_from_prerequisite("LSINF1121 ET LBIR1245A ET LDROI4578"),
                         ["LSINF1121", "LBIR1245A", "LDROI4578"])

        self.assertEqual(extract_learning_units_acronym_from_prerequisite("LSINF1121 OU LBIR1245A OU LDROI4578"),
                         ["LSINF1121", "LBIR1245A", "LDROI4578"])

    def test_when_prerequisites_multiple_learning_units_with_parentheses(self):
        self.assertEqual(extract_learning_units_acronym_from_prerequisite("LSINF1121 ET (LBIR1245A OU LDROI4578)"),
                         ["LSINF1121", "LBIR1245A", "LDROI4578"])

        self.assertEqual(extract_learning_units_acronym_from_prerequisite("(LSINF1121 ET LBIR1245A) OU LDROI4578"),
                         ["LSINF1121", "LBIR1245A", "LDROI4578"])

        self.assertEqual(
            extract_learning_units_acronym_from_prerequisite("(LSINF1121 ET LBIR1245A ET LMED1547) OU LDROI4578"),
            ["LSINF1121", "LBIR1245A", "LMED1547", "LDROI4578"])
