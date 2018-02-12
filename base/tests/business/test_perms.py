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
import factory.fuzzy
from django.test import TestCase
from base.tests.factories.academic_year import AcademicYearFactory

from base.business.learning_units import perms
from base.models.enums import learning_container_year_types
from base.models.enums.learning_unit_year_subtypes import FULL, PARTIM
from django.utils import timezone
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.learning_container_year import LearningContainerYearFactory


TYPES_PROPOSAL_NEEDED_TO_EDIT = (learning_container_year_types.COURSE,
                                 learning_container_year_types.DISSERTATION,
                                 learning_container_year_types.INTERNSHIP)

TYPES_DIRECT_EDIT_PERMITTED = (learning_container_year_types.OTHER_COLLECTIVE,
                               learning_container_year_types.OTHER_INDIVIDUAL,
                               learning_container_year_types.MASTER_THESIS,
                               learning_container_year_types.EXTERNAL)

ALL_TYPES = TYPES_PROPOSAL_NEEDED_TO_EDIT + TYPES_DIRECT_EDIT_PERMITTED


class PermsTestCase(TestCase):
    def setUp(self):
        self.academic_yr = AcademicYearFactory(year=timezone.now().year)

    def test_can_faculty_manager_modify_end_date_partim(self):
        for container_type in ALL_TYPES:
            lunit_container_yr = LearningContainerYearFactory(academic_year=self.academic_yr,
                                                              container_type=container_type)
            luy = LearningUnitYearFactory(academic_year=self.academic_yr,
                                          learning_container_year=lunit_container_yr,
                                          subtype=PARTIM)

            self.assertTrue(perms._can_faculty_manager_modify_end_date(luy))

    def test_can_faculty_manager_modify_end_date_full(self):
        for direct_edit_permitted_container_type in TYPES_DIRECT_EDIT_PERMITTED:
            lunit_container_yr = LearningContainerYearFactory(academic_year=self.academic_yr,
                                                              container_type=direct_edit_permitted_container_type)
            luy = LearningUnitYearFactory(academic_year=self.academic_yr,
                                          learning_container_year=lunit_container_yr,
                                          subtype=FULL)

            self.assertTrue(perms._can_faculty_manager_modify_end_date(luy))


    def test_cannot_faculty_manager_modify_end_date_full(self):
        for proposal_needed_container_type in TYPES_PROPOSAL_NEEDED_TO_EDIT:
            lunit_container_yr = LearningContainerYearFactory(academic_year=self.academic_yr,
                                                              container_type=proposal_needed_container_type)
            luy = LearningUnitYearFactory(academic_year=self.academic_yr,
                                          learning_container_year=lunit_container_yr,
                                          subtype=FULL)

            self.assertFalse(perms._can_faculty_manager_modify_end_date(luy))

    def test_cannot_faculty_manager_modify_end_date_no_container(self):
        luy = LearningUnitYearFactory(academic_year=self.academic_yr,
                                      learning_container_year=None)
        self.assertFalse(perms._can_faculty_manager_modify_end_date(luy))
