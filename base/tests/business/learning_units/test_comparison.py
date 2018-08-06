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

from base.models.learning_unit_year import LearningUnitYear, get_value
from base.business.learning_units.comparison import get_keys, translate, compare_learning_unit
from base.tests.factories.academic_year import create_current_academic_year, AcademicYearFactory
from base.tests.factories.learning_unit import LearningUnitFactory
from base.tests.factories.learning_unit_year import create_learning_unit_year

TITLE = 'Intitulé'
OTHER_TITLE = 'title 1'


class TestComparison(TestCase):
    def setUp(self):
        learning_unit = LearningUnitFactory()
        self.academic_year = create_current_academic_year()
        self.learning_unit_year = create_learning_unit_year(self.academic_year, TITLE, learning_unit)
        self.previous_academic_yr = AcademicYearFactory(year=self.academic_year.year - 1)
        self.previous_learning_unit_year = create_learning_unit_year(self.previous_academic_yr, OTHER_TITLE,
                                                                     learning_unit)

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

    def test_translate(self):
        self.assertIsNone(translate(None))

    def test_compare_learning_unit_with_nothing(self):
        self.academic_year_with_no_luy = AcademicYearFactory(year=self.academic_year.year - 2)
        self.assertEqual(compare_learning_unit(self.academic_year_with_no_luy, self.learning_unit_year), {})

    def test_compare_learning_unit(self):
        self.assertEqual(compare_learning_unit(self.previous_academic_yr, self.learning_unit_year),
                         {'specific_title': OTHER_TITLE})

