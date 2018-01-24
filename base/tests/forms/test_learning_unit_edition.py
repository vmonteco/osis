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

from base.business.learning_unit import LEARNING_UNIT_CREATION_SPAN_YEARS
from base.forms.learning_unit.edition import LearningUnitEndDateForm
from base.models import academic_year as mdl_academic_year
from base.models.academic_year import AcademicYear
from base.models.enums import learning_unit_periodicity
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.learning_container_year import LearningContainerYearFactory
from base.tests.factories.learning_unit import LearningUnitFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFakerFactory


class TestLearningUnitEditionForm(TestCase):

    def setUp(self):
        """
        Set up several learning units year associated with his learning unit,
        his learning container year and an academic year.
        """
        self._setup_academic_years()
        self._setup_learning_units()

    def _setup_academic_years(self):
        """
        We need at least seven academic years to have N+6 academic years,
        N being the current academic year.
        """
        self.this_year = datetime.datetime.now().year
        self.start_year = self.this_year - LEARNING_UNIT_CREATION_SPAN_YEARS
        self.last_year = self.this_year + LEARNING_UNIT_CREATION_SPAN_YEARS

        self.list_of_academic_years = self._create_list_of_academic_years(self.start_year, self.last_year)

        self.current_academic_year = mdl_academic_year.current_academic_year()
        self.oldest_academic_year = self.list_of_academic_years[0]
        self.last_academic_year = self.list_of_academic_years[-1]

        self.list_of_academic_years_after_now = [academic_year for academic_year in self.list_of_academic_years
                                                    if academic_year.year>=self.current_academic_year.year]
        self.list_of_odd_academic_years = [academic_year for academic_year in self.list_of_academic_years_after_now
                                                    if academic_year.year%2]
        self.list_of_even_academic_years = [academic_year for academic_year in self.list_of_academic_years_after_now
                                                    if not academic_year.year%2]

    def _setup_learning_units(self):
        self.learning_unit = LearningUnitFactory(start_year=self.current_academic_year.year,
                                                 periodicity=learning_unit_periodicity.ANNUAL)
        self.learning_container_year = LearningContainerYearFactory(academic_year=self.current_academic_year)
        self.learning_unit_year = LearningUnitYearFakerFactory(
            academic_year=self.current_academic_year,
            learning_unit=self.learning_unit,
            learning_container_year=self.learning_container_year)

    def _create_list_of_academic_years(self, start_year, end_year):
        results = [AcademicYearFactory.build(year=year) for year in range(start_year, end_year+1)]
        for result in results:
            super(AcademicYear, result).save()
        return results

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
        Fourth scenario: the end date is defined and the learning unit is annual
        """
        self.learning_unit.periodicity = learning_unit_periodicity.ANNUAL
        self.learning_unit.end_year = self.last_academic_year.year
        form = LearningUnitEndDateForm(None, learning_unit=self.learning_unit_year.learning_unit)
        self.assertEqual(list(form.fields['academic_year'].queryset), self.list_of_academic_years_after_now)

    def test_edit_end_date_send_dates_with_end_inferior_to_current_academic_year(self):
        """
        @:param request = GET (or None)
        Fith scenario: the end date is defined and the learning unit is annual
        """
        self.learning_unit.periodicity = learning_unit_periodicity.ANNUAL
        self.learning_unit.end_year = self.oldest_academic_year.year

        with self.assertRaises(ValueError):
            LearningUnitEndDateForm(None, learning_unit=self.learning_unit_year.learning_unit)

    def test_edit_end_date(self):
        """
        @:param request = POST
        Sixth scenario: the end date is edited
        """
        self.learning_unit.periodicity = learning_unit_periodicity.ANNUAL
        self.learning_unit.end_year = self.last_academic_year.year

        form_data = {"academic_year": self.current_academic_year.pk}

        form = LearningUnitEndDateForm(form_data, learning_unit=self.learning_unit)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['academic_year'], self.current_academic_year)
