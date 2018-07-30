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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################

from django.test import TestCase, RequestFactory
from django.urls import reverse

from base.templatetags.education_group import build_tree, NO_GIVEN_ROOT, BRANCH_TEMPLATE, ICON_JSTREE_FILE
from base.tests.factories.group_element_year import GroupElementYearFactory


class TestBuildTree(TestCase):
    maxDiff = None

    def setUp(self):
        self.group_element_year = GroupElementYearFactory()
        self.url = reverse("education_group_read", args=[self.group_element_year.child_branch.pk])
        self.context = {
            "request": RequestFactory().get(self.url)
        }

    def test_invalid_tree(self):
        result = build_tree(context=self.context,
                            current_group_element_year=None,
                            selected_education_group_year=None)
        self.assertEqual(result, NO_GIVEN_ROOT)

    def test_valid_tree_only_root(self):
        result = build_tree(
            context=self.context,
            current_group_element_year=self.group_element_year,
            selected_education_group_year=self.group_element_year.child_branch
        )

        self.assertHTMLEqual(result, self._expect_result(self.group_element_year))

    def test_valid_tree_with_children(self):
        group_element_year_child_1 = GroupElementYearFactory(parent=self.group_element_year.child_branch)
        group_element_year_child_1_1 = GroupElementYearFactory(parent=group_element_year_child_1.child_branch)
        group_element_year_child_1_2 = GroupElementYearFactory(parent=group_element_year_child_1.child_branch)
        group_element_year_child_2 = GroupElementYearFactory(parent=self.group_element_year.child_branch)

        result = build_tree(
            context=self.context,
            current_group_element_year=self.group_element_year,
            selected_education_group_year=self.group_element_year.child_branch
        )

        self.assertHTMLEqual(result, self._expect_result(self.group_element_year))

    def _expect_result(self, gey, root=True):
        sub_templates = ""
        for el in gey.child_branch.group_element_year_branches:
            sub_templates += self._expect_result(el, False)

        return BRANCH_TEMPLATE.format(
            data_jstree=ICON_JSTREE_FILE if not gey.child_branch.group_element_year_branches else "",
            gey=gey.pk,
            egy=gey.child_branch.pk,
            url=reverse("education_group_read", args=[gey.child_branch.pk]) + "?root=&group_to_parent=" + str(gey.pk),
            text=gey.child_branch.verbose,
            a_class="jstree-wholerow-clicked" if root else "",
            children=sub_templates
        )
