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

from base.tests.factories.business.learning_units import LearningUnitsMixin


class TestLearningUnitEdition(TestCase, LearningUnitsMixin):
    """
    WARNING: the user cannot edit a learning unit whith a end date
    inferior to the current academic year!

    General cases :
        1. end_date_inferior_to_current_academic_year
        2. end_date_superior_to_current_academic_year

    Case 1 : end_date_inferior_to_current_academic_year
        We must delete learning units,
        from the new edited end date to the old end date.
        -

    Case 2 : end_date_superior_to_current_academic_year
        We must create learning units,
        from the old end date to the new edited end date
        - check the subtype : either Partim or Full.
        -
    """

    def setUp(self):
        super().setUp()
        self.setup_academic_years()
        self.learning_unit = self.setup_learning_unit(self.current_academic_year.year)
        self.learning_container_year = self.setup_learning_container_year(self.current_academic_year)
        self.learning_unit_year = self.setup_learning_unit_year(
            self.current_academic_year,
            self.learning_unit,
            self.learning_container_year
        )

    def test_edit_end_date_inferior_to_current_academic_year(self):
        """
        """
        pass

    def test_edit_learning_unit_end_date_with_start_date_inferior_to_current_academic_year_and_subtype_is_full(self):
        """
        The en date before editing is the current academic year incremented by one;
        example:
        - save the new end date
        - create new learning units in the future
        - goal : end date is saved and learning units exists from start date to end date
        """
        self.learning_unit.start_year = self.current_academic_year.year - 1
        self.learning_unit.end_year = self.current_academic_year.year + 1

        self.list_of_learning_unit_years = self.setup_list_of_learning_unit_years(
            self.list_of_academic_years_after_now,
            self.learning_unit
        )
        print('TEST 1:')
        print(self.list_of_learning_unit_years)

    def test_edit_learning_unit_end_date_with_start_date_superior_to_current_academic_year_and_subtype_is_full(self):
        """
        The en date before editing is the current academic year incremented by one;
        example:
        - save the new end date
        - create new learning units in the future
        - goal : end date is saved and learning units exists from start date to end date
        """
        self.learning_unit.start_year = self.current_academic_year.year + 1
        self.learning_unit.end_year = self.current_academic_year.year + 2

        self.list_of_learning_unit_years = self.setup_list_of_learning_unit_years(
            self.list_of_academic_years_after_now,
            self.learning_unit
        )

        print('TEST 2:')
        print(self.list_of_learning_unit_years)

