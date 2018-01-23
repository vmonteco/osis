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

from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.learning_container_year import LearningContainerYearFactory
from base.tests.factories.learning_unit import LearningUnitFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFakerFactory


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

        today = datetime.date.today()
        self.current_academic_year = AcademicYearFactory(
            start_date=today,
            end_date=today.replace(year=today.year + 1),
            year=today.year)
        self.start_year = self.current_academic_year.year
        self.last_year = self.current_academic_year.year + 6

        #The first learning unit has a starting date equal to the current academic year N
        self.learning_unit = LearningUnitFactory(start_year=self.current_academic_year.year)
        self.list_of_academic_years = self._create_list_of_academic_years(self.start_year, self.last_year)
        self.learning_container_year = LearningContainerYearFactory(academic_year=self.current_academic_year)
        self.learning_unit_year = LearningUnitYearFakerFactory(
            academic_year=self.current_academic_year,
            learning_unit=self.learning_unit,
            learning_container_year=self.learning_container_year)

    def _create_list_of_academic_years(self, start_year, end_year):
        return [AcademicYearFactory(year=year) for year in range(start_year, end_year+1)]

    def test_edit_end_date_send_dates_with_end_date_not_defined_yet(self):
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
        form = LearningUnitEditionForm(None, learning_unit=self.learning_unit_year.learning_unit)
        self.assertIsHaha(form.hoho)

    def test_edit_end_date_send_non_biennal_dates(self):
        """
        """
        pass

    def test_edit_end_date_send_biennal_even_dates(self):
        """
        """
        pass

    def test_edit_end_date_send_biennal_odd_dates(self):
        """
        """
        pass
