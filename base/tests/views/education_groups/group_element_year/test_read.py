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
from django.http import HttpResponseRedirect
from django.test import TestCase
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from base.models.learning_component_year import LearningComponentYear, volume_total_verbose
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.group_element_year import GroupElementYearFactory
from base.tests.factories.learning_component_year import LearningComponentYearFactory
from base.tests.factories.learning_unit_component import LearningUnitComponentFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.user import SuperUserFactory
from base.views.education_groups.group_element_year.read import get_verbose_children


class TestRead(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.person = PersonFactory()
        cls.education_group_year_1 = EducationGroupYearFactory()
        cls.education_group_year_2 = EducationGroupYearFactory()
        cls.education_group_year_3 = EducationGroupYearFactory()
        cls.learning_unit_year_1 = LearningUnitYearFactory()
        cls.learning_unit_year_2 = LearningUnitYearFactory()
        cls.learning_component_year_1 = LearningComponentYearFactory(
            learning_container_year=cls.learning_unit_year_1.learning_container_year, hourly_volume_partial_q1=10,
            hourly_volume_partial_q2=10)
        cls.learning_component_year_2 = LearningComponentYearFactory(
            learning_container_year=cls.learning_unit_year_1.learning_container_year, hourly_volume_partial_q1=10,
            hourly_volume_partial_q2=10)
        cls.learning_unit_component_1 = LearningUnitComponentFactory(
            learning_component_year=cls.learning_component_year_1,
            learning_unit_year=cls.learning_unit_year_1)
        cls.learning_unit_component_2 = LearningUnitComponentFactory(
            learning_component_year=cls.learning_component_year_2,
            learning_unit_year=cls.learning_unit_year_1)
        cls.group_element_year_1 = GroupElementYearFactory(parent=cls.education_group_year_1,
                                                           child_branch=cls.education_group_year_2)
        cls.group_element_year_2 = GroupElementYearFactory(parent=cls.education_group_year_2,
                                                           child_branch=None,
                                                           child_leaf=cls.learning_unit_year_1)
        cls.group_element_year_3 = GroupElementYearFactory(parent=cls.education_group_year_1,
                                                           child_branch=cls.education_group_year_3)
        cls.group_element_year_4 = GroupElementYearFactory(parent=cls.education_group_year_3,
                                                           child_branch=None,
                                                           child_leaf=cls.learning_unit_year_2)
        cls.a_superuser = SuperUserFactory()

    def test_pdf_content(self):
        url = reverse("pdf_content", args=[self.education_group_year_1.id, self.education_group_year_1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, HttpResponseRedirect.status_code)

    def test_get_verbose_children(self):
        result = get_verbose_children(self.education_group_year_1)
        context_waiting = [self.group_element_year_1, [self.group_element_year_2], self.group_element_year_3,
                           [self.group_element_year_4]]
        self.assertEqual(result, context_waiting)

        verbose_branch = _("%(title)s (%(credits)s credits)") % {
            "title": self.group_element_year_1.child.title,
            "credits": self.group_element_year_1.relative_credits or self.group_element_year_1.child_branch.credits or 0
        }
        self.assertEqual(self.group_element_year_1.verbose, verbose_branch)

        components = LearningComponentYear.objects.filter(
            learningunitcomponent__learning_unit_year=self.group_element_year_2.child_leaf
        )
        verbose_leaf = _("%(acronym)s %(title)s [%(volumes)s] (%(credits)s credits)") % {
            "acronym": self.group_element_year_2.child_leaf.acronym,
            "title": self.group_element_year_2.child_leaf.specific_title,
            "volumes": volume_total_verbose(components),
            "credits": self.group_element_year_2.relative_credits or self.group_element_year_2.child_leaf.credits or 0
        }
        self.assertEqual(self.group_element_year_2.verbose, verbose_leaf)
