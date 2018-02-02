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
from django.utils import timezone
from attribution.models import attribution
from base.models import learning_unit_year
from base.models.enums import learning_unit_year_subtypes
from base.tests.factories.learning_unit import LearningUnitFactory
from base.tests.factories.tutor import TutorFactory
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory, create_learning_units_year
from base.tests.factories.learning_container_year import LearningContainerYearFactory


class LearningUnitYearTest(TestCase):
    def setUp(self):
        self.tutor = TutorFactory()
        self.academic_year = AcademicYearFactory(year=timezone.now().year)
        self.learning_unit_year = LearningUnitYearFactory(acronym="LDROI1004", title="Juridic law courses",
                                                          academic_year=self.academic_year)

    def test_find_by_tutor_with_none_argument(self):
        self.assertEquals(attribution.find_by_tutor(None), None)

    def test_subdivision_computation(self):
        l_container_year = LearningContainerYearFactory(acronym="LBIR1212", academic_year=self.academic_year)
        l_unit_1 = LearningUnitYearFactory(acronym="LBIR1212", learning_container_year=l_container_year,
                                           academic_year=self.academic_year)
        l_unit_2 = LearningUnitYearFactory(acronym="LBIR1212A", learning_container_year=l_container_year,
                                           academic_year=self.academic_year)
        l_unit_3 = LearningUnitYearFactory(acronym="LBIR1212B", learning_container_year=l_container_year,
                                           academic_year=self.academic_year)

        self.assertFalse(l_unit_1.subdivision)
        self.assertEqual(l_unit_2.subdivision, 'A')
        self.assertEqual(l_unit_3.subdivision, 'B')

    def test_search_acronym_by_regex(self):
        regex_valid = '^LD.+1+'
        query_result_valid = learning_unit_year.search(acronym=regex_valid)
        self.assertEqual(len(query_result_valid), 1)
        self.assertEqual(self.learning_unit_year.acronym, query_result_valid[0].acronym)

    def test_property_in_charge(self):
        self.assertFalse(self.learning_unit_year.in_charge)

        a_container_year = LearningContainerYearFactory(acronym=self.learning_unit_year.acronym,
                                                        academic_year=self.academic_year)
        self.learning_unit_year.learning_container_year = a_container_year

        self.assertFalse(self.learning_unit_year.in_charge)

        a_container_year.in_charge = True

        self.assertTrue(self.learning_unit_year.in_charge)

    def test_find_gte_learning_units_year(self):
        learning_unit = LearningUnitFactory()
        dict_learning_unit_year = create_learning_units_year(2000, 2017, learning_unit)

        selected_learning_unit_year = dict_learning_unit_year[2007]

        result = list(selected_learning_unit_year.find_gte_learning_units_year().values_list('academic_year__year',
                                                                                             flat=True))
        self.assertListEqual(result, list(range(2007,2018)))

    def test_find_gte_learning_units_year_case_no_future(self):
        learning_unit = LearningUnitFactory()
        dict_learning_unit_year = create_learning_units_year(2000, 2017, learning_unit)

        selected_learning_unit_year = dict_learning_unit_year[2017]

        result = list(selected_learning_unit_year.find_gte_learning_units_year().values_list('academic_year__year',
                                                                                             flat=True))
        self.assertEqual(result, [2017])

    def test_get_learning_unit_parent(self):
        lunit_container_year = LearningContainerYearFactory(academic_year=self.academic_year, acronym='LBIR1230')
        luy_parent = LearningUnitYearFactory(academic_year=self.academic_year, acronym='LBIR1230',
                                             learning_container_year=lunit_container_year,
                                             subtype=learning_unit_year_subtypes.FULL)
        luy_partim = LearningUnitYearFactory(academic_year=self.academic_year, acronym='LBIR1230B',
                                             learning_container_year=lunit_container_year,
                                             subtype=learning_unit_year_subtypes.PARTIM)
        self.assertEqual(luy_partim.parent, luy_parent)

    def test_get_learning_unit_parent_without_parent(self):
        lunit_container_year = LearningContainerYearFactory(academic_year=self.academic_year, acronym='LBIR1230')
        luy_parent = LearningUnitYearFactory(academic_year=self.academic_year, acronym='LBIR1230',
                                             learning_container_year=lunit_container_year,
                                             subtype=learning_unit_year_subtypes.FULL)
        self.assertIsNone(luy_parent.parent)