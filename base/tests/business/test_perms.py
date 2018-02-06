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
from base.tests.factories.academic_year import AcademicYearFactory

from base.business.learning_units import perms
from base.models.enums.learning_container_year_types import COURSE, MASTER_THESIS
from base.models.enums.learning_unit_year_subtypes import PARTIM
from django.utils import timezone
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.learning_container_year import LearningContainerYearFactory


class PermsTestCase(TestCase):
    def setUp(self):
        self.academic_yr = AcademicYearFactory(year=timezone.now().year)

    def test_can_faculty_manager_modify_end_date_course_partim(self):
        lunit_container_yr = LearningContainerYearFactory(academic_year=self.academic_yr,
                                                          container_type=COURSE)
        luy = LearningUnitYearFactory(academic_year=self.academic_yr,
                                      learning_container_year=lunit_container_yr,
                                      subtype=PARTIM)

        self.assertTrue(perms._can_faculty_manager_modify_end_date(luy))

    def test_can_faculty_manager_modify_end_date_not_course_partim(self):
        lunit_container_yr = LearningContainerYearFactory(academic_year=self.academic_yr,
                                                          container_type=MASTER_THESIS)
        luy = LearningUnitYearFactory(academic_year=self.academic_yr,
                                      learning_container_year=lunit_container_yr)

        self.assertTrue(perms._can_faculty_manager_modify_end_date(luy))

    def test_cannot_faculty_manager_modify_end_date(self):
        luy = LearningUnitYearFactory(academic_year=self.academic_yr,
                                      learning_container_year=None,
                                      subtype=PARTIM)
        self.assertFalse(perms._can_faculty_manager_modify_end_date(luy))
