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

from base.forms.learning_unit.edition import LearningUnitEndDateForm
from base.models.enums import learning_unit_periodicity, learning_unit_year_subtypes
from base.tests.factories.business.learning_units import LearningUnitsMixin


class TestLearningUnitEditionForm(TestCase, LearningUnitsMixin):

    def setUp(self):
        super().setUp()
        self.setup_academic_years()
        self.learning_unit = self.setup_learning_unit(self.current_academic_year.year)
        self.learning_container_year = self.setup_learning_container_year(self.current_academic_year)
        self.learning_unit_year = self.setup_learning_unit_year(
            self.current_academic_year,
            self.learning_unit,
            self.learning_container_year,
            learning_unit_year_subtypes.FULL
        )

    def test_edit_end_date_send_dates_with_end_date_not_defined(self):
        """
        @:param request = GET (or None)
        @:return list of annual academic years from the current academic year to six years later

        The user wants to edit the end date of a learning unit.
        All the valid years from the start date to the end date
        are send to the view.

        First scenario: the end date is not defined yet and the learning unit is annual.
        Which means that all the possible end dates must be stricly superior
        to the current academic year N (end_dates > N) and equal or inferior to N+6 (en_dates =< N+6)
        In other words : N < end_dates =< N+6
        """
        form = LearningUnitEndDateForm(None, learning_unit=self.learning_unit_year.learning_unit)
        self.assertEqual(list(form.fields['academic_year'].queryset), self.list_of_academic_years_after_now)

    def test_edit_end_date_send_dates_with_end_date_not_defined_and_periodicity_biennal_even(self):
        """
        @:param request = GET (or None)
        @:return list of biennal even academic years from the current academic year to six years later

        Second scenario: the end date is not defined yet and the learning unit is biennal even.
        """
        self.learning_unit.periodicity = learning_unit_periodicity.BIENNIAL_EVEN
        form = LearningUnitEndDateForm(None, learning_unit=self.learning_unit_year.learning_unit)
        self.assertEqual(list(form.fields['academic_year'].queryset), self.list_of_even_academic_years)

    def test_edit_end_date_send_dates_with_end_date_not_defined_and_periodicity_biennal_odd(self):
        """
        @:param request = GET (or None)
        @:return list of biennal odd academic years from the current academic year to six years later

        Third scenario: the end date is not defined yet and the learning unit is biennal odd.
        """
        self.learning_unit.periodicity = learning_unit_periodicity.BIENNIAL_ODD
        form = LearningUnitEndDateForm(None, learning_unit=self.learning_unit_year.learning_unit)
        self.assertEqual(list(form.fields['academic_year'].queryset), self.list_of_odd_academic_years)

    def test_edit_end_date_send_dates_with_end_date_defined(self):
        """
        @:param request = GET (or None)
        Fourth scenario: the end date is defined and the learning unit is annual.
        The end date of the learning unit is set to an academic year superior
        to the current academic year.
        Warning: the number of academic years presented to the user as always a maxium value of N+6.
        Example: the current year is 2018 (N), but the learning unit as a start date of 2020 (X);
        we cannot propose 2020 to 2026 (X+6) but 2024 to 2024 (N +6).
        """
        self.learning_unit.end_year = self.last_academic_year.year
        form = LearningUnitEndDateForm(None, learning_unit=self.learning_unit_year.learning_unit)
        self.assertEqual(list(form.fields['academic_year'].queryset), self.list_of_academic_years_after_now)

    def test_edit_end_date_send_dates_with_end_date_of_learning_unit_inferior_to_current_academic_year(self):
        """
        @:param request = GET (or None)
        Fith scenario: the end date is defined and the learning unit is annual
        BUT the end date of the learning unit is already passed.
        The user cannot change the end date of a learning unit for which
        the end date is inferior to the current academic year.
        """
        self.learning_unit.end_year = self.oldest_academic_year.year
        with self.assertRaises(ValueError):
            LearningUnitEndDateForm(None, learning_unit=self.learning_unit_year.learning_unit)

    def test_edit_end_date(self):
        """
        @:param request = POST
        @:param request = the form and his data
        @:param request = the learning unit for which the end date must be changed
        Sixth scenario: the end date of a learning unit is edited.
        We need to be verify the validation of the form, nothing else.
        """
        self.learning_unit.end_year = self.last_academic_year.year
        form_data = {"academic_year": self.current_academic_year.pk}
        form = LearningUnitEndDateForm(form_data, learning_unit=self.learning_unit)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['academic_year'], self.current_academic_year)

    def test_edit_end_date_with_end_date_before_start_date(self):
        """
        :return:
        """
        self.fail('Finish the test!')
