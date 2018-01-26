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

from base.business.learning_units.edition import edit_learning_unit_end_date
from base.models import academic_year
from base.models.enums import learning_unit_year_subtypes, learning_unit_periodicity
from base.models.learning_unit_year import LearningUnitYear
from base.tests.factories.business.learning_units import LearningUnitsMixin


class TestLearningUnitEdition(TestCase, LearningUnitsMixin):
    """
    WARNING: the user cannot edit a learning unit whith a end date
    inferior to the current academic year!

    General cases :
        1. test_edit_learning_unit_full_annual_end_date_with_start_date_gt_now
        2. test_edit_learning_unit_partim_annual_end_date_with_start_date_gt_now

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
        self.learning_container_year_course = self.setup_learning_container_year(self.current_academic_year)

    def test_edit_learning_unit_full_annual_end_date_with_start_date_gt_now(self):
        """
        Start date = 2018
        Current date = 2017
        End date = 2019
        New end date = 2020
        """
        learning_unit_full_annual = self.setup_learning_unit(
            start_year=self.current_academic_year.year,
            periodicity=learning_unit_periodicity.ANNUAL
        )

        learning_unit_full_annual.start_year = self.current_academic_year.year + 2
        learning_unit_full_annual.end_year = self.current_academic_year.year + 4
        learning_unit_full_annual.save()

        self.setup_list_of_learning_unit_years(
            list_of_academic_years=self.list_of_academic_years_after_now,
            learning_unit=learning_unit_full_annual,
            learning_container_year=self.learning_container_year_course,
            learning_unit_year_subtype=learning_unit_year_subtypes.FULL
        )

        list_of_expected_learning_unit_years = []
        for learning_unit_year in list(LearningUnitYear.objects.all()):
            list_of_expected_learning_unit_years.append(learning_unit_year.academic_year.year)
        list_of_expected_learning_unit_years.append(learning_unit_full_annual.end_year+1)
        list_of_expected_learning_unit_years.append(learning_unit_full_annual.end_year+2)

        academic_year_of_new_end_date = academic_year.find_academic_year_by_year(
            learning_unit_full_annual.end_year+2
        )
        edit_learning_unit_end_date(learning_unit_full_annual, academic_year_of_new_end_date)

        list_of_learning_unit_years = []
        for learning_unit_year in list(LearningUnitYear.objects.all()):
            list_of_learning_unit_years.append(learning_unit_year.academic_year.year)
        self.assertEqual(sorted(list_of_learning_unit_years), sorted(list_of_learning_unit_years))

    def test_edit_learning_unit_partim_annual_end_date_with_start_date_gt_now(self):
        """
        Current date = 2017
        Start date = 2018
        End date = 2019
        New end date = 2020
        """
        learning_unit_full_annual = self.setup_learning_unit(
            start_year=self.current_academic_year.year,
            periodicity=learning_unit_periodicity.ANNUAL
        )
        learning_unit_partim_annual = self.setup_learning_unit(
            start_year=self.current_academic_year.year,
            periodicity=learning_unit_periodicity.ANNUAL
        )
        #6
        learning_unit_full_annual.start_year = self.current_academic_year.year + 1
        learning_unit_full_annual.end_year = self.current_academic_year.year + 6
        learning_unit_full_annual.save()
        #2
        learning_unit_partim_annual.start_year = self.current_academic_year.year + 2
        learning_unit_partim_annual.end_year = self.current_academic_year.year + 3
        learning_unit_partim_annual.save()

        list_of_learning_unit_years_full_annual = self.setup_list_of_learning_unit_years(
            list_of_academic_years=self.list_of_academic_years_after_now,
            learning_unit=learning_unit_full_annual,
            learning_container_year=self.learning_container_year_course,
            learning_unit_year_subtype=learning_unit_year_subtypes.FULL
        )
        list_of_learning_unit_years_partim_annual = self.setup_list_of_learning_unit_years(
            list_of_academic_years=self.list_of_academic_years_after_now,
            learning_unit=learning_unit_partim_annual,
            learning_container_year=self.learning_container_year_course,
            learning_unit_year_subtype=learning_unit_year_subtypes.PARTIM
        )

        list_of_expected_learning_unit_years = []
        for learning_unit_year_expected in list_of_learning_unit_years_partim_annual:
            list_of_expected_learning_unit_years.append(learning_unit_year_expected.academic_year.year)
        list_of_expected_learning_unit_years.append(learning_unit_partim_annual.end_year+1)
        list_of_expected_learning_unit_years.append(learning_unit_partim_annual.end_year+2)

        academic_year_of_new_end_date = academic_year.find_academic_year_by_year(
            learning_unit_partim_annual.end_year+2)

        #Method to test
        edit_learning_unit_end_date(learning_unit_partim_annual, academic_year_of_new_end_date)

        list_of_learning_unit_years_full = []
        list_of_learning_unit_years_partim = []
        list_of_all_learning_unit_years = list(LearningUnitYear.objects.all())

        for learning_unit_year_saved in list_of_all_learning_unit_years:
            if learning_unit_year_saved.get_partims_related():
                list_of_learning_unit_years_full.append(learning_unit_year_saved.academic_year.year)
            else:
                list_of_learning_unit_years_partim.append(learning_unit_year_saved.academic_year.year)

        self.assertEqual(len(list_of_learning_unit_years_full), len(list_of_learning_unit_years_full_annual))
        self.assertEqual(len(list_of_learning_unit_years_partim), len(list_of_expected_learning_unit_years))
        self.assertEqual(sorted(list_of_learning_unit_years_partim), sorted(list_of_expected_learning_unit_years))

    def test_edit_learning_unit_end_date_with_start_date_gt_now_and_is_partim_and_parent_end_date_lt_new_end_date(self):
        """

        :return:
        """
        pass

    def test_edit_learning_unit_end_date_with_new_end_date_gt_end_date_and_subtype_is_full(self):
        """
        Start date = 2016
        Current date = 2017
        End date = 2018
        New end date = 2020
        """
        self.fail('Finish the test!')

    def test_edit_learning_unit_end_date_with_new_end_date_gt_end_date_and_subtype_is_partim(self):
        """
        Start date = 2016
        Current date = 2017
        End date = 2018
        New end date = 2020
        """
        self.fail('Finish the test!')

    def test_edit_learning_unit_end_date_with_new_end_date_lt_end_date_and_subtype_is_full(self):
        """
        Start date = 2018
        Current date = 2017
        End date = 2019
        New end date = 2020
        """
        self.fail('Finish the test!')

    def test_edit_learning_unit_end_date_with_new_end_date_lt_end_date_and_subtype_is_partim(self):
        """
        Start date = 2018
        Current date = 2017
        End date = 2019
        New end date = 2020
        """
        self.fail('Finish the test!')

    def test_edit_learning_unit_end_date_with_new_end_date_is_none_and_subtype_is_full(self):
        """
        Start date = 2018
        Current date = 2017
        End date = 2019
        New end date = 2020
        """
        self.fail('Finish the test!')

    def test_edit_learning_unit_end_date_with_new_end_date_is_none_and_subtype_is_partim(self):
        """
        Start date = 2018
        Current date = 2017
        End date = 2019
        New end date = 2020
        """
        self.fail('Finish the test!')
