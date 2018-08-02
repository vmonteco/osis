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
from django.test.utils import override_settings

from base.models.learning_unit_year import LearningUnitYear
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.academic_year import create_current_academic_year
from base.business.learning_units.comparison import get_value, get_keys
from base.models.enums import learning_unit_year_subtypes

TITLE = 'Intitulé'


class TestComparison(TestCase):
    def setUp(self):
        self.academic_year = create_current_academic_year()
        self.learning_unit_year = LearningUnitYearFactory(
            academic_year=self.academic_year,
            subtype=learning_unit_year_subtypes.FULL,
            status=True,
            specific_title=TITLE

        )

    @override_settings(LANGUAGES=[('fr-be', 'French'), ('en', 'English'), ], LANGUAGE_CODE='fr-be')
    def test_get_value_for_boolean(self):
        data = self.learning_unit_year.__dict__
        self.assertEqual(get_value(LearningUnitYear, data, 'status'), 'Oui')

    @override_settings(LANGUAGES=[('fr-be', 'French'), ('en', 'English'), ], LANGUAGE_CODE='fr-be')
    def test_get_value_for_enum(self):
        data = self.learning_unit_year.__dict__
        self.assertEqual(get_value(LearningUnitYear, data, 'subtype'), 'Complet')

    @override_settings(LANGUAGES=[('fr-be', 'French'), ('en', 'English'), ], LANGUAGE_CODE='fr-be')
    def test_get_value(self):
        data = self.learning_unit_year.__dict__
        self.assertEqual(get_value(LearningUnitYear, data, 'specific_title'), TITLE)

    def test_get_keys(self):
        self.assertCountEqual(get_keys(['a1', 'c3'], ['a1', 'b2', 'c1']), ['a1', 'b2', 'c1', 'c3'])
