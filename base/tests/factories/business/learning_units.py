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

from base.business.learning_unit import LEARNING_UNIT_CREATION_SPAN_YEARS, compute_max_academic_year_adjournment
from base.models import academic_year as mdl_academic_year
from base.models.academic_year import AcademicYear
from base.models.enums import entity_container_year_link_type, learning_container_year_types, learning_unit_periodicity, \
    learning_unit_year_subtypes
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.entity_container_year import EntityContainerYearFactory
from base.tests.factories.learning_container_year import LearningContainerYearFactory
from base.tests.factories.learning_unit import LearningUnitFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory


def create_learning_unit_with_context(academic_year, structure, entity, acronym):
    learning_container_year = LearningContainerYearFactory(academic_year=academic_year, acronym=acronym)
    learning_unit_year = LearningUnitYearFactory(structure=structure,
                                                 acronym=acronym,
                                                 learning_container_year=learning_container_year,
                                                 academic_year=academic_year)

    EntityContainerYearFactory(type=entity_container_year_link_type.ALLOCATION_ENTITY,
                               learning_container_year=learning_container_year,
                               entity=entity)

    return learning_unit_year


class LearningUnitsMixin:
    this_year = start_year = last_year = current_academic_year = None
    old_academic_year = last_academic_year = oldest_academic_year = latest_academic_year = None
    learning_unit = learning_unit_year = learning_container_year = None
    list_of_academic_years = []
    list_of_academic_years_after_now = []
    list_of_odd_academic_years = []
    list_of_even_academic_years = []
    list_of_learning_units = []
    list_of_learning_container_year = []
    list_of_learning_unit_years = []

    def setup_academic_years(self):
        self.this_year = datetime.datetime.now().year
        self.start_year = self.this_year - LEARNING_UNIT_CREATION_SPAN_YEARS * 2
        self.last_year = self.this_year + LEARNING_UNIT_CREATION_SPAN_YEARS * 2

        self.list_of_academic_years = self.create_list_of_academic_years(self.start_year, self.last_year)

        self.current_academic_year = mdl_academic_year.current_academic_year()
        index_of_current_academic_year_in_list = self.list_of_academic_years.index(self.current_academic_year)

        self.oldest_academic_year = self.list_of_academic_years[0]
        self.latest_academic_year = self.list_of_academic_years[-1]
        self.old_academic_year = self.list_of_academic_years[index_of_current_academic_year_in_list -
                                                             LEARNING_UNIT_CREATION_SPAN_YEARS]
        self.last_academic_year = self.list_of_academic_years[index_of_current_academic_year_in_list +
                                                              LEARNING_UNIT_CREATION_SPAN_YEARS]

        self.list_of_academic_years_after_now = [
            academic_year for academic_year in self.list_of_academic_years
            if (self.current_academic_year.year <= academic_year.year <= self.last_academic_year.year)
        ]
        self.list_of_odd_academic_years = [academic_year for academic_year in self.list_of_academic_years_after_now
                                           if academic_year.year % 2]
        self.list_of_even_academic_years = [academic_year for academic_year in self.list_of_academic_years_after_now
                                            if not academic_year.year % 2]

    @staticmethod
    def create_list_of_academic_years(start_year, end_year):
        results = None
        if start_year and end_year:
            results = [AcademicYearFactory.build(year=year) for year in range(start_year, end_year + 1)]
            for result in results:
                super(AcademicYear, result).save()
        return results

    @staticmethod
    def setup_learning_unit(start_year, periodicity=learning_unit_periodicity.ANNUAL, end_year=None):
        result = None
        if start_year:
            result = LearningUnitFactory(
                start_year=start_year,
                periodicity=periodicity,
                end_year=end_year)
        return result

    @staticmethod
    def setup_learning_container_year(academic_year, container_type):
        result = None
        if academic_year and container_type:
            result = LearningContainerYearFactory(
                academic_year=academic_year,
                container_type=container_type
            )
        return result

    @staticmethod
    def setup_learning_unit_year(academic_year, learning_unit, learning_container_year, learning_unit_year_subtype):
        create = False
        result = None
        end_year = learning_unit.end_year or compute_max_academic_year_adjournment()
        if learning_unit.start_year <= academic_year.year <= end_year:
            if learning_unit.periodicity == learning_unit_periodicity.BIENNIAL_ODD:
                if not (academic_year.year % 2):
                    create = True
            elif learning_unit.periodicity == learning_unit_periodicity.BIENNIAL_EVEN:
                if academic_year.year % 2:
                    create = True
            elif learning_unit.periodicity == learning_unit_periodicity.ANNUAL:
                    create = True

            if create:
                if not learning_container_year:
                    learning_container_year = LearningUnitsMixin.setup_learning_container_year(
                        academic_year, learning_container_year_types.COURSE
                    )

                result = LearningUnitYearFactory(
                    acronym=learning_unit.acronym,
                    academic_year=academic_year,
                    learning_unit=learning_unit,
                    learning_container_year=learning_container_year,
                    subtype=learning_unit_year_subtype
                )
        return result

    @staticmethod
    def setup_list_of_learning_unit_years_full(list_of_academic_years, learning_unit_full):
        results = []
        if not list_of_academic_years or not learning_unit_full:
            return results

        for academic_year in list_of_academic_years:
            results.append(
                LearningUnitsMixin.setup_learning_unit_year(
                    academic_year=academic_year,
                    learning_unit=learning_unit_full,
                    learning_container_year=None,
                    learning_unit_year_subtype=learning_unit_year_subtypes.FULL
                )
            )
        return results

    @staticmethod
    def setup_list_of_learning_unit_years_partim(list_of_academic_years, learning_unit_full, learning_unit_partim):
        results = []
        if not list_of_academic_years or not learning_unit_full or not learning_unit_partim:
            return results

        for academic_year in list_of_academic_years:

            learning_unit_year_full = LearningUnitsMixin.setup_learning_unit_year(
                academic_year=academic_year,
                learning_unit=learning_unit_full,
                learning_container_year=None,
                learning_unit_year_subtype=learning_unit_year_subtypes.FULL
            )

            if learning_unit_year_full:
                results.append(learning_unit_year_full)

                learning_unit_year_partim = LearningUnitsMixin.setup_learning_unit_year(
                    academic_year=academic_year,
                    learning_unit=learning_unit_partim,
                    learning_container_year=learning_unit_year_full.learning_container_year,
                    learning_unit_year_subtype=learning_unit_year_subtypes.PARTIM
                )
                if learning_unit_year_partim:
                    results.append(learning_unit_year_partim)

        return results
