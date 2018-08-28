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
from unittest import skip

from django.core.exceptions import ValidationError
from django.test import TestCase
from base.models.prerequisite import prerequisite_syntax_validator


class TestPrerequisiteSyntaxValidator(TestCase):
    @skip("Wait to see is validator is applied on empty string")
    def test_empty_string(self):
        self.assertIsNone(prerequisite_syntax_validator(""))

    def test_with_one_prerequisite_badly_encoded(self):
        test_values = (
            "LSINF 1111",
            "1452 LINGI",
            "LILKNLJLJFD48464",
            "LI12",
            "LSINF 1256 BD",
            "lsinf1111a",
            "LINGI2154B",
        )
        for test_value in test_values:
            with self.subTest(bad_prerequisite=test_value):
                with self.assertRaises(ValidationError):
                    prerequisite_syntax_validator(test_value)
