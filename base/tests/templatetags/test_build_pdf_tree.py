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
from django.template import Context, Template
from django.test import TestCase

from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.group_element_year import GroupElementYearFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.views.education_groups.group_element_year.read import get_verbose_children


class TestBuildPDFTree(TestCase):
    def setUp(self):
        self.education_group_year_1 = EducationGroupYearFactory(credits=10)
        self.education_group_year_2 = EducationGroupYearFactory(credits=20)
        self.learning_unit_year_1 = LearningUnitYearFactory()
        self.group_element_year_1 = GroupElementYearFactory(parent=self.education_group_year_1,
                                                            child_branch=self.education_group_year_2,
                                                            is_mandatory=True)
        self.group_element_year_2 = GroupElementYearFactory(parent=self.education_group_year_2,
                                                            child_branch=None,
                                                            child_leaf=self.learning_unit_year_1,
                                                            is_mandatory=True)

    def test_build_pdf_tree_with_mandatory(self):
        tree = get_verbose_children(self.education_group_year_1)
        out = Template(
            "{% load education_group %}"
            "{{ tree|pdf_tree_list }}"
        ).render(Context({
            'tree': tree
        }))
        self.assertEqual(out,
                         str('<tr><td style="padding-left:2em;width:580px;"><img '
                             'src="/static/img/education_group_year/mandatory.png" height="10" width="10">{}<tr>'
                             '<td style="padding-left:4em;width:580px;">'
                             '<img src="/static/img/education_group_year/case.jpg" height="14" width="17">'
                             '<img src="/static/img/education_group_year/mandatory.png" height="10" '
                             'width="10">{}</td><td style="width:15px;text-align: center;"></td>'
                             '<td style="width:15px;text-align: center;"></td>'
                             '<td style="width:15px;text-align: center;">'
                             '</td></tr></td></tr>').format(
                             self.education_group_year_2.verbose_credit, self.group_element_year_2.verbose))

    def test_build_pdf_tree_with_optional(self):
        self.group_element_year_1.is_mandatory = False
        self.group_element_year_1.save()
        self.group_element_year_2.is_mandatory = False
        self.group_element_year_2.save()

        tree = get_verbose_children(self.education_group_year_1)
        out = Template(
            "{% load education_group %}"
            "{{ tree|pdf_tree_list }}"
        ).render(Context({
            'tree': tree
        }))
        self.assertEqual(out,
                         str('<tr><td style="padding-left:2em;width:580px;"><img '
                             'src="/static/img/education_group_year/optional.png" height="10" width="10">{}<tr>'
                             '<td style="padding-left:4em;width:580px;">'
                             '<img src="/static/img/education_group_year/case.jpg" height="14" width="17">'
                             '<img src="/static/img/education_group_year/optional.png" height="10" '
                             'width="10">{}</td><td style="width:15px;text-align: center;"></td>'
                             '<td style="width:15px;text-align: center;"></td>'
                             '<td style="width:15px;text-align: center;">'
                             '</td></tr></td></tr>').format(
                             self.education_group_year_2.verbose_credit, self.group_element_year_2.verbose))

    def test_tree_list_with_none(self):
        out = Template(
            "{% load education_group %}"
            "{{ tree|pdf_tree_list }}"
        ).render(Context({
            'tree': None
        }))
        self.assertEqual(out, "")

    def test_tree_list_with_empty(self):
        out = Template(
            "{% load education_group %}"
            "{{ tree|pdf_tree_list }}"
        ).render(Context({
            'tree': []
        }))
        self.assertEqual(out, "")
