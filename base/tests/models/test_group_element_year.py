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
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.group_element_year import GroupElementYearFactory
from base.models import group_element_year


class GroupElementYearTest(TestCase):

    def test_find_by_parent(self):
        academic_year = AcademicYearFactory()

        education_group_year_parent = EducationGroupYearFactory(academic_year=academic_year)

        education_group_branch_1 = EducationGroupYearFactory(academic_year=academic_year)
        education_group_brancg_2 = EducationGroupYearFactory(academic_year=academic_year)

        group_element_year_1 = GroupElementYearFactory(parent=education_group_year_parent,
                                                       child_branch=education_group_branch_1)
        group_element_year_2 = GroupElementYearFactory(parent=education_group_year_parent,
                                                       child_branch=education_group_brancg_2)

        self.assertCountEqual(group_element_year.find_by_parent(education_group_year_parent), [group_element_year_1, group_element_year_2])






