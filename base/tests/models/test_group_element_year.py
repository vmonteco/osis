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
from base.models.enums import education_group_categories
from base.models.group_element_year import GroupElementYear
from base.tests.factories.education_group_type import EducationGroupTypeFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from django.test import TestCase
from base.tests.factories.academic_year import AcademicYearFactory, create_current_academic_year
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.group_element_year import GroupElementYearFactory
from base.models import group_element_year


def build_hierarchy():
    current_academic_year = create_current_academic_year()
    root_group_type = EducationGroupTypeFactory(name='Bachelor', category=education_group_categories.TRAINING)
    root = EducationGroupYearFactory(academic_year=current_academic_year, education_group_type=root_group_type)
    for _ in range(3):
        group_type = EducationGroupTypeFactory(category=education_group_categories.GROUP)
        educ_group = EducationGroupYearFactory(academic_year=current_academic_year, education_group_type=group_type)
        GroupElementYearFactory(parent=root, child_branch=educ_group)
        for __ in range(3):
            GroupElementYearFactory(parent=educ_group, child_branch=None, child_leaf=LearningUnitYearFactory())
    return root


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


class TestFindBuildParentListByEducationGroupYearId(TestCase):
    """Unit tests for _build_parent_list_by_education_group_year_id() function"""
    def setUp(self):
        current_academic_year = create_current_academic_year()
        root_group_type = EducationGroupTypeFactory(name='Bachelor', category=education_group_categories.TRAINING)
        self.root = EducationGroupYearFactory(academic_year=current_academic_year, education_group_type=root_group_type)

        group_type = EducationGroupTypeFactory(category=education_group_categories.GROUP)
        self.child_branch = EducationGroupYearFactory(academic_year=current_academic_year, education_group_type=group_type)
        GroupElementYearFactory(parent=self.root, child_branch=self.child_branch)

        self.child_leaf = LearningUnitYearFactory(academic_year=current_academic_year)
        GroupElementYearFactory(parent=self.child_branch, child_branch=None, child_leaf=self.child_leaf)

    def test_with_filters(self):
        self.maxDiff = None
        filters = {
            'parent__education_group_type__category': [education_group_categories.TRAINING]
        }
        result = group_element_year._build_parent_list_by_education_group_year_id(self.child_leaf, filters=filters)

        expected_result = {
            'child_branch_{}'.format(self.child_branch.id): [{
                'parent': self.root.id,
                'child_branch': self.child_branch.id,
                'child_leaf': None,
                'parent__education_group_type__category': self.root.education_group_type.category
            },],
            'child_leaf_{}'.format(self.child_leaf.id): [{
                'parent': self.child_branch.id,
                'child_branch': None,
                'child_leaf': self.child_leaf.id,
                'parent__education_group_type__category': self.child_branch.education_group_type.category
            },]
        }
        self.assertEqual(len(result), len(expected_result))
        self.assertDictEqual(result, expected_result)

    def test_without_filters(self):
        result = group_element_year._build_parent_list_by_education_group_year_id(self.child_leaf)
        expected_result = {
            'child_branch_{}'.format(self.child_branch.id): [{
                'parent': self.root.id,
                'child_branch': self.child_branch.id,
                'child_leaf': None,
            },],
            'child_leaf_{}'.format(self.child_leaf.id): [{
                'parent': self.child_branch.id,
                'child_branch': None,
                'child_leaf': self.child_leaf.id,
            },]
        }
        self.assertEqual(len(result), len(expected_result))
        self.assertDictEqual(result, expected_result)


class TestFindRelatedRootEducationGroups(TestCase):
    """Unit tests for _find_related_root_education_groups() function"""
    def setUp(self):
        current_academic_year = create_current_academic_year()
        self.child_leaf = LearningUnitYearFactory(academic_year=current_academic_year)

        root_group_type = EducationGroupTypeFactory(name='Bachelor', category=education_group_categories.TRAINING)
        self.root = EducationGroupYearFactory(academic_year=current_academic_year, education_group_type=root_group_type)

    def test_without_filters_case_direct_parent_id_root(self):
        element_year = GroupElementYearFactory(parent=self.root, child_branch=None, child_leaf=self.child_leaf)
        result = group_element_year._find_related_root_education_groups(self.child_leaf)
        self.assertEqual(result, [element_year.parent.id])

    def test_without_filters_case_parent_in_2nd_level(self):
        pass

    def test_without_filters_case_multiple_parents_in_2nd_level(self):
        pass