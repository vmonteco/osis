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

from base.business.learning_unit import LEARNING_UNIT_CREATION_SPAN_YEARS
from base.models import academic_year as mdl_academic_year
from base.models.academic_year import AcademicYear
from base.models.enums import entity_container_year_link_type, learning_unit_periodicity
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.entity_container_year import EntityContainerYearFactory
from base.tests.factories.learning_container_year import LearningContainerYearFactory
from base.tests.factories.learning_unit import LearningUnitFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFakerFactory


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
    list_of_academic_years = list_of_academic_years_after_now = None
    list_of_odd_academic_years = list_of_even_academic_years = None
    learning_unit = learning_unit_year = learning_container_year = None
    list_of_learning_units = list_of_learning_unit_years = None

    def setup_academic_years(self):
        """
        Set up academic years from (N - LEARNING_UNIT_CREATION_SPAN_YEARS) to (N + LEARNING_UNIT_CREATION_SPAN_YEARS),
        N being the current academic year.
        Ex : from 2012-2013 to 2024-2025, N being 2018-2019.

        From this list we create three lists :
         - a list with annual academic years from N to (N + LEARNING_UNIT_CREATION_SPAN_YEARS);
         - a list with biennal even academic years from  N to (N + LEARNING_UNIT_CREATION_SPAN_YEARS);
         - a list with viennal odd academic years from from N to (N + LEARNING_UNIT_CREATION_SPAN_YEARS).
        """
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

        self.list_of_academic_years_after_now = [academic_year for academic_year in self.list_of_academic_years
                                                 if (
                                                 self.current_academic_year.year <= academic_year.year <= self.last_academic_year.year)]
        self.list_of_odd_academic_years = [academic_year for academic_year in self.list_of_academic_years_after_now
                                           if academic_year.year % 2]
        self.list_of_even_academic_years = [academic_year for academic_year in self.list_of_academic_years_after_now
                                            if not academic_year.year % 2]

    def setup_learning_unit(self):
        """
        Set up a learning unit associated with a learning container and a learning unit year.
        By default, the learning unit start year is the current academic year and the periodicity is annual.
        """
        self.learning_unit = LearningUnitFactory(
            start_year=self.current_academic_year.year,
            periodicity=learning_unit_periodicity.ANNUAL)

    def setup_list_of_learning_units(self, number):
        for i in range(0, number):
            self.list_of_learning_units[i] = LearningUnitFactory(
                start_year=self.current_academic_year.year,
                periodicity=learning_unit_periodicity.ANNUAL)

    def setup_learning_container_year(self):
        self.learning_container_year = LearningContainerYearFactory(academic_year=self.current_academic_year)

    def setup_learning_unit_year(self):
        self.learning_unit_year = LearningUnitYearFakerFactory(
                academic_year=self.current_academic_year,
                learning_unit=self.learning_unit,
                learning_container_year=self.learning_container_year)

    def setup_list_of_learning_unit_years(self, learning_unit, learning_container_year):
        """
        Given a learning unit, generate a set of learning units years,
        from the start date to the end date of the associated learning unit.
        :param learning_unit: a learning unit associated to the learning unit
        :param learning_container_year: a learning unit container
        :return: list of learning units created
        """
        self.list_of_learning_unit_years = [
            LearningUnitYearFakerFactory(
                academic_year=x,
                learning_unit=learning_unit,
                learning_container_year=learning_container_year)
            for x in range(learning_unit.start_date, learning_unit.end_date + 1)
            ]

    @staticmethod
    def create_list_of_academic_years(start_year, end_year):
        results = [AcademicYearFactory.build(year=year) for year in range(start_year, end_year + 1)]
        for result in results:
            super(AcademicYear, result).save()
        return results
