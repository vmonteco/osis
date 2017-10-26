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

from base.models import learning_container_year
from base.models.enums import learning_unit_year_subtypes
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.learning_container_year import LearningContainerYearFactory
from base.tests.factories.learning_unit_enrollment import LearningUnitEnrollmentFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from django.utils import timezone


class LearningContainerYearTest(TestCase):
    def setUp(self):
        self.academic_year = AcademicYearFactory(year=timezone.now().year)

    def test_find_by_id_with_id(self):
        l_container_year = LearningContainerYearFactory()
        self.assertEqual(l_container_year, learning_container_year.find_by_id(l_container_year.id))

    def test_find_by_id_with_wrong_value(self):
        with self.assertRaises(ValueError):
            learning_container_year.find_by_id("BAD VALUE")

    def test_is_deletable(self):
        l_container_year = LearningContainerYearFactory()
        l_unit_1 = LearningUnitYearFactory(acronym="LBIR1212", learning_container_year=l_container_year,
                                           academic_year=self.academic_year, subtype=learning_unit_year_subtypes.FULL)
        msg = []
        self.assertTrue(l_container_year.is_deletable(msg))
        self.assertListEqual(msg, [])

        l_unit_2 = LearningUnitYearFactory(acronym="LBIR1212", learning_container_year=l_container_year,
                                           academic_year=self.academic_year, subtype=learning_unit_year_subtypes.PARTIM)

        LearningUnitEnrollmentFactory()
        l_container_year.is_deletable(msg)
        print(msg)
        self.assertEqual(msg[0], '-> Error : a partim LBIR1212 is linked to the learning unit ')
