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

from django.db import IntegrityError
from django.test import TestCase

from base.business.learning_units.edition import edit_learning_unit_end_date
from base.models import academic_year
from base.models.enums import learning_unit_year_subtypes, learning_unit_periodicity
from base.models.learning_unit_year import LearningUnitYear
from base.tests.factories.business.learning_units import LearningUnitsMixin
from base.tests.factories.learning_unit import LearningUnitFactory


class TestLearningUnitEdition(TestCase, LearningUnitsMixin):
    """
    General cases :

        The start date of the learning unit is greater than current academic year
        Only test the ANNUAL periodicity (the BIENNAL periodicity is covered later on)
        The new end date of the learning unit is greater than old end date (creation)
        01. test_edit_learning_unit_full_annual_end_date_gt_old_end_date_with_start_date_gt_now
        02. test_edit_learning_unit_partim_annual_end_date_gt_old_end_date_with_start_date_gt_now

        The start date of the learning unit is less than current academic year
        The new end date of the learning unit is greater than old end date (creation)
        03. test_edit_learning_unit_full_annual_end_date_gt_old_end_date_with_start_date_lt_now
        04. test_edit_learning_unit_full_odd_end_date_gt_old_end_date_with_start_date_lt_now
        05. test_edit_learning_unit_full_even_end_date_gt_old_end_date_with_start_date_lt_now
        06. test_edit_learning_unit_partim_annual_end_gt_old_end_date_date_with_start_date_lt_now

        The new end date of the learning unit is none (creation)
        07. test_edit_learning_unit_full_annual_end_date_is_none_with_start_date_lt_now
        08. test_edit_learning_unit_partim_annual_end_date_is_none_with_start_date_lt_now
        09. test_edit_learning_unit_partim_annual_end_date_is_none_with_start_date_lt_now_with_error

        The new end date of the learning unit is less than old end date (deletion)
        10. test_edit_learning_unit_full_annual_end_date_lt_old_end_date_with_start_date_lt_now
        11. test_edit_learning_unit_full_odd_end_date_lt_old_end_date_with_start_date_lt_now
        12. test_edit_learning_unit_full_even_end_date_lt_old_end_date_with_start_date_lt_now
        13. test_edit_learning_unit_partim_annual_end_date_lt_old_end_date_with_start_date_lt_now
    """

    def setUp(self):
        super().setUp()
        self.setup_academic_years()
        self.learning_container_year_course = self.setup_learning_container_year(self.current_academic_year)

    def test_edit_learning_unit_full_annual_end_date_gt_old_end_date_with_start_date_gt_now(self):
        """
        """
        learning_unit_full_annual = self.setup_learning_unit(
            start_year=self.current_academic_year.year,
            periodicity=learning_unit_periodicity.ANNUAL
        )

        learning_unit_full_annual.start_year = self.current_academic_year.year + 1
        learning_unit_full_annual.end_year = self.current_academic_year.year + 3
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
        list_of_expected_learning_unit_years.append(learning_unit_full_annual.end_year + 1)
        list_of_expected_learning_unit_years.append(learning_unit_full_annual.end_year + 2)

        academic_year_of_new_end_date = academic_year.find_academic_year_by_year(
            learning_unit_full_annual.end_year + 2
        )
        edit_learning_unit_end_date(learning_unit_full_annual, academic_year_of_new_end_date)

        list_of_learning_unit_years = []
        for learning_unit_year in list(LearningUnitYear.objects.all()):
            list_of_learning_unit_years.append(learning_unit_year.academic_year.year)
        self.assertEqual(sorted(list_of_learning_unit_years), sorted(list_of_expected_learning_unit_years))

    def test_edit_learning_unit_partim_annual_end_date_gt_old_end_date_with_start_date_gt_now(self):
        """
        """
        learning_unit_full_annual = self.setup_learning_unit(
            start_year=self.current_academic_year.year,
            periodicity=learning_unit_periodicity.ANNUAL
        )
        learning_unit_partim_annual = self.setup_learning_unit(
            start_year=self.current_academic_year.year,
            periodicity=learning_unit_periodicity.ANNUAL
        )
        learning_unit_full_annual.start_year = self.current_academic_year.year + 1
        learning_unit_full_annual.end_year = self.current_academic_year.year + 6
        learning_unit_full_annual.save()
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
        list_of_expected_learning_unit_years.append(learning_unit_partim_annual.end_year + 1)
        list_of_expected_learning_unit_years.append(learning_unit_partim_annual.end_year + 2)

        academic_year_of_new_end_date = academic_year.find_academic_year_by_year(
            learning_unit_partim_annual.end_year + 2)

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
        self.assertEqual(sorted(list_of_learning_unit_years_partim), sorted(list_of_expected_learning_unit_years))

    def test_edit_learning_unit_full_annual_end_date_gt_old_end_date_with_start_date_lt_now(self):
        """
        """
        learning_unit_full_annual = self.setup_learning_unit(
            start_year=self.current_academic_year.year,
            periodicity=learning_unit_periodicity.ANNUAL
        )

        learning_unit_full_annual.start_year = self.current_academic_year.year - 1
        learning_unit_full_annual.end_year = self.current_academic_year.year + 1
        learning_unit_full_annual.save()

        self.setup_list_of_learning_unit_years(
            list_of_academic_years=self.list_of_academic_years,
            learning_unit=learning_unit_full_annual,
            learning_container_year=self.learning_container_year_course,
            learning_unit_year_subtype=learning_unit_year_subtypes.FULL
        )

        list_of_expected_learning_unit_years = []
        for learning_unit_year in list(LearningUnitYear.objects.all()):
            list_of_expected_learning_unit_years.append(learning_unit_year.academic_year.year)
        list_of_expected_learning_unit_years.append(learning_unit_full_annual.end_year + 1)
        list_of_expected_learning_unit_years.append(learning_unit_full_annual.end_year + 2)

        academic_year_of_new_end_date = academic_year.find_academic_year_by_year(
            learning_unit_full_annual.end_year + 2
        )
        edit_learning_unit_end_date(learning_unit_full_annual, academic_year_of_new_end_date)

        list_of_learning_unit_years = []
        for learning_unit_year in list(LearningUnitYear.objects.all()):
            list_of_learning_unit_years.append(learning_unit_year.academic_year.year)
        self.assertEqual(sorted(list_of_learning_unit_years), sorted(list_of_expected_learning_unit_years))

    def test_edit_learning_unit_full_odd_end_date_gt_old_end_date_with_start_date_lt_now(self):
        """
        """
        learning_unit_full_annual = self.setup_learning_unit(
            start_year=self.current_academic_year.year,
            periodicity=learning_unit_periodicity.BIENNIAL_ODD
        )

        learning_unit_full_annual.start_year = self.current_academic_year.year - 2
        learning_unit_full_annual.end_year = self.current_academic_year.year + 2
        learning_unit_full_annual.save()

        self.setup_list_of_learning_unit_years(
            list_of_academic_years=self.list_of_academic_years,
            learning_unit=learning_unit_full_annual,
            learning_container_year=self.learning_container_year_course,
            learning_unit_year_subtype=learning_unit_year_subtypes.FULL
        )

        list_of_expected_learning_unit_years = []
        for learning_unit_year in list(LearningUnitYear.objects.all()):
            list_of_expected_learning_unit_years.append(learning_unit_year.academic_year.year)
        if self.current_academic_year.year % 2:
            list_of_expected_learning_unit_years.append(learning_unit_full_annual.end_year + 2)
        else:
            list_of_expected_learning_unit_years.append(learning_unit_full_annual.end_year + 1)

        academic_year_of_new_end_date = academic_year.find_academic_year_by_year(
            learning_unit_full_annual.end_year + 2
        )
        edit_learning_unit_end_date(learning_unit_full_annual, academic_year_of_new_end_date)

        list_of_learning_unit_years = []
        for learning_unit_year in list(LearningUnitYear.objects.all()):
            list_of_learning_unit_years.append(learning_unit_year.academic_year.year)
        self.assertEqual(sorted(list_of_learning_unit_years), sorted(list_of_expected_learning_unit_years))

    def test_edit_learning_unit_full_even_end_date_gt_old_end_date_with_start_date_lt_now(self):
        """
        """
        learning_unit_full_annual = self.setup_learning_unit(
            start_year=self.current_academic_year.year,
            periodicity=learning_unit_periodicity.BIENNIAL_EVEN
        )

        learning_unit_full_annual.start_year = self.current_academic_year.year - 2
        learning_unit_full_annual.end_year = self.current_academic_year.year + 2
        learning_unit_full_annual.save()

        self.setup_list_of_learning_unit_years(
            list_of_academic_years=self.list_of_academic_years,
            learning_unit=learning_unit_full_annual,
            learning_container_year=self.learning_container_year_course,
            learning_unit_year_subtype=learning_unit_year_subtypes.FULL
        )

        list_of_expected_learning_unit_years = []
        for learning_unit_year in list(LearningUnitYear.objects.all()):
            list_of_expected_learning_unit_years.append(learning_unit_year.academic_year.year)
        if self.current_academic_year.year % 2:
            list_of_expected_learning_unit_years.append(learning_unit_full_annual.end_year + 1)
        else:
            list_of_expected_learning_unit_years.append(learning_unit_full_annual.end_year + 2)

        academic_year_of_new_end_date = academic_year.find_academic_year_by_year(
            learning_unit_full_annual.end_year + 2
        )
        edit_learning_unit_end_date(learning_unit_full_annual, academic_year_of_new_end_date)

        list_of_learning_unit_years = []
        for learning_unit_year in list(LearningUnitYear.objects.all()):
            list_of_learning_unit_years.append(learning_unit_year.academic_year.year)
        self.assertEqual(sorted(list_of_learning_unit_years), sorted(list_of_expected_learning_unit_years))

    def test_edit_learning_unit_partim_annual_end_gt_old_end_date_date_with_start_date_lt_now(self):
        """
        """
        learning_unit_full_annual = self.setup_learning_unit(
            start_year=self.current_academic_year.year,
            periodicity=learning_unit_periodicity.ANNUAL
        )
        learning_unit_partim_annual = self.setup_learning_unit(
            start_year=self.current_academic_year.year,
            periodicity=learning_unit_periodicity.ANNUAL
        )
        learning_unit_full_annual.start_year = self.current_academic_year.year - 1
        learning_unit_full_annual.end_year = self.current_academic_year.year + 3
        learning_unit_full_annual.save()
        learning_unit_partim_annual.start_year = self.current_academic_year.year - 1
        learning_unit_partim_annual.end_year = self.current_academic_year.year + 1
        learning_unit_partim_annual.save()

        list_of_learning_unit_years_full_annual = self.setup_list_of_learning_unit_years(
            list_of_academic_years=self.list_of_academic_years,
            learning_unit=learning_unit_full_annual,
            learning_container_year=self.learning_container_year_course,
            learning_unit_year_subtype=learning_unit_year_subtypes.FULL
        )
        list_of_learning_unit_years_partim_annual = self.setup_list_of_learning_unit_years(
            list_of_academic_years=self.list_of_academic_years,
            learning_unit=learning_unit_partim_annual,
            learning_container_year=self.learning_container_year_course,
            learning_unit_year_subtype=learning_unit_year_subtypes.PARTIM
        )

        list_of_expected_learning_unit_years = []
        for learning_unit_year_expected in list_of_learning_unit_years_partim_annual:
            list_of_expected_learning_unit_years.append(learning_unit_year_expected.academic_year.year)
        list_of_expected_learning_unit_years.append(learning_unit_partim_annual.end_year + 1)
        list_of_expected_learning_unit_years.append(learning_unit_partim_annual.end_year + 2)

        academic_year_of_new_end_date = academic_year.find_academic_year_by_year(
            learning_unit_partim_annual.end_year + 2)

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
        self.assertEqual(sorted(list_of_learning_unit_years_partim), sorted(list_of_expected_learning_unit_years))

    def test_edit_learning_unit_full_annual_end_date_is_none_with_start_date_lt_now(self):
        """
        """
        learning_unit_full_annual = self.setup_learning_unit(
            start_year=self.current_academic_year.year,
            periodicity=learning_unit_periodicity.ANNUAL
        )

        learning_unit_full_annual.start_year = self.current_academic_year.year - 1
        learning_unit_full_annual.end_year = self.current_academic_year.year + 4
        learning_unit_full_annual.save()

        self.setup_list_of_learning_unit_years(
            list_of_academic_years=self.list_of_academic_years,
            learning_unit=learning_unit_full_annual,
            learning_container_year=self.learning_container_year_course,
            learning_unit_year_subtype=learning_unit_year_subtypes.FULL
        )

        list_of_expected_learning_unit_years = []
        for learning_unit_year in list(LearningUnitYear.objects.all()):
            list_of_expected_learning_unit_years.append(learning_unit_year.academic_year.year)
        list_of_expected_learning_unit_years.append(learning_unit_full_annual.end_year + 1)
        list_of_expected_learning_unit_years.append(learning_unit_full_annual.end_year + 2)

        academic_year_of_new_end_date = None

        edit_learning_unit_end_date(learning_unit_full_annual, academic_year_of_new_end_date)

        list_of_learning_unit_years = []
        for learning_unit_year in list(LearningUnitYear.objects.all()):
            list_of_learning_unit_years.append(learning_unit_year.academic_year.year)
        self.assertEqual(sorted(list_of_learning_unit_years), sorted(list_of_expected_learning_unit_years))

    def test_edit_learning_unit_partim_annual_end_date_is_none_with_start_date_lt_now(self):
        """
        """
        learning_unit_full_annual = self.setup_learning_unit(
            start_year=self.current_academic_year.year,
            periodicity=learning_unit_periodicity.ANNUAL
        )
        learning_unit_partim_annual = self.setup_learning_unit(
            start_year=self.current_academic_year.year,
            periodicity=learning_unit_periodicity.ANNUAL
        )
        learning_unit_full_annual.start_year = self.current_academic_year.year - 1
        learning_unit_full_annual.end_year = self.current_academic_year.year + 6
        learning_unit_full_annual.save()
        learning_unit_partim_annual.start_year = self.current_academic_year.year - 1
        learning_unit_partim_annual.end_year = self.current_academic_year.year + 4
        learning_unit_partim_annual.save()

        list_of_learning_unit_years_full_annual = self.setup_list_of_learning_unit_years(
            list_of_academic_years=self.list_of_academic_years,
            learning_unit=learning_unit_full_annual,
            learning_container_year=self.learning_container_year_course,
            learning_unit_year_subtype=learning_unit_year_subtypes.FULL
        )
        list_of_learning_unit_years_partim_annual = self.setup_list_of_learning_unit_years(
            list_of_academic_years=self.list_of_academic_years,
            learning_unit=learning_unit_partim_annual,
            learning_container_year=self.learning_container_year_course,
            learning_unit_year_subtype=learning_unit_year_subtypes.PARTIM
        )

        list_of_expected_learning_unit_years = []
        for learning_unit_year_expected in list_of_learning_unit_years_partim_annual:
            list_of_expected_learning_unit_years.append(learning_unit_year_expected.academic_year.year)
        list_of_expected_learning_unit_years.append(learning_unit_partim_annual.end_year + 1)
        list_of_expected_learning_unit_years.append(learning_unit_partim_annual.end_year + 2)

        academic_year_of_new_end_date = None

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
        self.assertEqual(sorted(list_of_learning_unit_years_partim), sorted(list_of_expected_learning_unit_years))

    def test_edit_learning_unit_partim_annual_end_date_is_none_with_start_date_lt_now_with_error(self):
        """
        """
        learning_unit_full_annual = self.setup_learning_unit(
            start_year=self.current_academic_year.year,
            periodicity=learning_unit_periodicity.ANNUAL
        )
        learning_unit_partim_annual = self.setup_learning_unit(
            start_year=self.current_academic_year.year,
            periodicity=learning_unit_periodicity.ANNUAL
        )
        learning_unit_full_annual.start_year = self.current_academic_year.year - 1
        learning_unit_full_annual.end_year = self.current_academic_year.year + 4
        learning_unit_full_annual.save()
        learning_unit_partim_annual.start_year = self.current_academic_year.year -1
        learning_unit_partim_annual.end_year = self.current_academic_year.year + 2
        learning_unit_partim_annual.save()

        self.setup_list_of_learning_unit_years(
            list_of_academic_years=self.list_of_academic_years,
            learning_unit=learning_unit_full_annual,
            learning_container_year=self.learning_container_year_course,
            learning_unit_year_subtype=learning_unit_year_subtypes.FULL
        )
        self.setup_list_of_learning_unit_years(
            list_of_academic_years=self.list_of_academic_years,
            learning_unit=learning_unit_partim_annual,
            learning_container_year=self.learning_container_year_course,
            learning_unit_year_subtype=learning_unit_year_subtypes.PARTIM
        )

        academic_year_of_new_end_date = None

        with self.assertRaises(IntegrityError):
            edit_learning_unit_end_date(learning_unit_partim_annual, academic_year_of_new_end_date)

    def test_edit_learning_unit_full_annual_end_date_lt_old_end_date_with_start_date_lt_now(self):
        """
        """
        self.fail('Finish the test!')

    def test_edit_learning_unit_full_odd_end_date_lt_old_end_date_with_start_date_lt_now(self):
        """
        """
        self.fail('Finish the test!')

    def test_edit_learning_unit_full_even_end_date_lt_old_end_date_with_start_date_lt_now(self):
        """
        """
        self.fail('Finish the test!')

    def test_edit_learning_unit_partim_annual_end_date_lt_old_end_date_with_start_date_lt_now(self):
        """
        """
        self.fail('Finish the test!')
