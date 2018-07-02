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
from base.models.education_group_type import EducationGroupType, find_authorized_types
from base.tests.factories.education_group_type import EducationGroupTypeFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.unauthorized_relationship import UnauthorizedRelationshipFactory
from django.test import TestCase
from base.models.enums import education_group_categories


class TestAuthorizedTypes(TestCase):
    """Unit tests on find_authorized_types()"""
    def setUp(self):
        self.category = education_group_categories.GROUP

        self.subgroup = EducationGroupTypeFactory(name='Subgroup', category=self.category)
        self.complementary_module = EducationGroupTypeFactory(name='Complementary module', category=self.category)
        self.options_list = EducationGroupTypeFactory(name='Options list', category=self.category)

    def test_ordered_by_name(self):
        EducationGroupTypeFactory(category=education_group_categories.TRAINING)
        expected_result = [self.complementary_module, self.options_list, self.subgroup]
        self.assertEqual(expected_result, list(find_authorized_types(category=self.category)))

    def test_filter_on_authorized_types(self):
        doctorate = EducationGroupTypeFactory(name='PhD', category=education_group_categories.TRAINING)
        UnauthorizedRelationshipFactory(parent_type=doctorate, child_type=self.options_list)
        educ_group_year = EducationGroupYearFactory(education_group_type=doctorate)
        result = find_authorized_types(parent_education_group_year=educ_group_year)
        self.assertEqual(len(result), 3)
        self.assertNotIn(self.options_list, result)

    def test_when_no_unauthorized_type_matches(self):
        UnauthorizedRelationshipFactory(parent_type=self.complementary_module, child_type=self.options_list)
        educ_group_year = EducationGroupYearFactory(education_group_type=self.subgroup)
        result = find_authorized_types(parent_education_group_year=educ_group_year)
        self.assertEqual(result.count(), EducationGroupType.objects.filter(category=self.subgroup.category).count())

    def test_all_types_returned_when_no_filters_given(self):
        """If no category and no parent is given, then the function should return all education group types"""
        result = find_authorized_types()
        self.assertNotEqual(list(result), [])
        self.assertEqual(len(result), EducationGroupType.objects.all().count())
