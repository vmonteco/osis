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

from base.forms.learning_unit.edition import LearningUnitEndDateForm
from base.models.academic_year import AcademicYear
from base.models.enums import learning_unit_periodicity
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.learning_container_year import LearningContainerYearFactory
from base.tests.factories.learning_unit import LearningUnitFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFakerFactory
from base.views.learning_unit import LEARNING_UNIT_CREATION_SPAN_YEARS


class TestLearningUnitEditionForm(TestCase):

    def setUp(self):
        """
        Set up several learning units year associated with his learning unit,
        his learning container year and an academic year.

        We need at least seven academic years to have N+6 academic years,
        N being the current academic year.

        We need some specific learnign units as describe below:
            1. A learning unit associated to a start date only
            2. A learning unit associated to a start date and a end_date
        :return: self
        """

        self.today = datetime.date.today()

        #TODO: refactor self.start_year
        self.start_year = self.today.year if self.today.month>9 and self.today.month<12 else self.today.year-1
        self.last_year = self.start_year + LEARNING_UNIT_CREATION_SPAN_YEARS

        self.list_of_academic_years = self._create_list_of_academic_years(self.start_year, self.last_year)
        self.current_academic_year = self.list_of_academic_years[0]

        for academic_year in self.list_of_academic_years:
            if academic_year.year%2:
                self.list_of_academic_years_biennal_odd = academic_year
            else:
                self.list_of_academic_years_biennal_even = academic_year

        self.list_of_odd_academic_years = [academic_year for academic_year in self.list_of_academic_years
                                                    if academic_year.year%2]
        self.list_of_even_academic_years = [academic_year for academic_year in self.list_of_academic_years
                                                    if not academic_year.year%2]

        #The first learning unit has a starting date equal to the current academic year N
        self.learning_unit = LearningUnitFactory(start_year=self.today.year,
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
        @:param request : GET (request = None)
        @:return list of non biennal academic years from the current academic year to six years later

        The user wants to edit the end date of a learning unit.
        All the valid years from the start date to the end date
        are send to the view.

        First scenario: the end date is not defined yet.
        Which means that all the possible end dates must be stricly superior
        to the current academic year N (end_dates > N) and equal or inferior to N+6 (en_dates =< N+6)
        In other words : N < end_dates =< N+6
        """
        form = LearningUnitEndDateForm(None, learning_unit=self.learning_unit_year.learning_unit)
        self.assertEqual(list(form.fields['academic_year'].queryset), self.list_of_academic_years)

    def test_edit_end_date_send_dates_with_end_date_not_defined_and_periodicity_biennal_even(self):
        """
        @:param request : GET (request = None)
        @:return list of non biennal academic years from the current academic year to six years later
        """
        self.learning_unit.periodicity = learning_unit_periodicity.BIENNIAL_EVEN
        form = LearningUnitEndDateForm(None, learning_unit=self.learning_unit_year.learning_unit)
        self.assertEqual(list(form.fields['academic_year'].queryset), self.list_of_even_academic_years)

    def test_edit_end_date_send_dates_with_end_date_not_defined_and_periodicity_biennal_odd(self):
        """
        @:param request : GET (request = None)
        @:return list of non biennal academic years from the current academic year to six years later
        """
        self.learning_unit.periodicity = learning_unit_periodicity.BIENNIAL_ODD
        form = LearningUnitEndDateForm(None, learning_unit=self.learning_unit_year.learning_unit)
        self.assertEqual(list(form.fields['academic_year'].queryset), self.list_of_odd_academic_years)
