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
import datetime

from django.test import TestCase
from django.urls import reverse

from base.models.tutor import Tutor
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.tutor import TutorFactory

from attribution.tests.factories.attribution import AttributionFactory
from attribution.views.manage_my_courses import list_my_attributions_summary_editable


HTTP_NOT_FOUND = 404


class ManageMyCoursesViewTestCase(TestCase):
    def setUp(self):
        self.person = PersonFactory()
        self.user = self.person.user
        self.tutor = TutorFactory(person=self.person)
        self.academic_year = AcademicYearFactory(year=datetime.date.today().year,
                                                 start_date=datetime.date.today())

        self.learning_unit_years = [LearningUnitYearFactory(summary_editable=True)
                                    for i in range(4)]
        self.attributions = [AttributionFactory(tutor=self.tutor,
                                                summary_responsible=True,
                                                learning_unit_year=self.learning_unit_years[i])
                             for i in range(4)]

    def test_list_my_attributions_summary_editable_user_not_logged(self):
        url = reverse(list_my_attributions_summary_editable)
        self.client.logout()
        response = self.client.get(url)
        self.assertRedirects(response, '/login/?next={}'.format(url))

    def test_list_my_attributions_summary_editable_user_not_tutor(self):
        tutors = Tutor.objects.filter(person__user=self.user)
        tutors.delete()

        self.client.force_login(self.user)
        url = reverse(list_my_attributions_summary_editable)
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, HTTP_NOT_FOUND)

    def test_list_my_attributions_summary_editable(self):
        self.client.force_login(self.user)
        url = reverse(list_my_attributions_summary_editable)
        response = self.client.get(url)
        self.assertTemplateUsed(response, "manage_my_courses/list_my_courses_summary_editable.html")

        context = response.context[-1]
        self.assertCountEqual(context['learning_unit_years_summary_editable'], self.learning_unit_years)


    def test_list_my_attributions_summary_editable_false_for_some(self):
        self.client.force_login(self.user)

        self.learning_unit_years[0].summary_editable = False
        self.learning_unit_years[0].save()
        self.learning_unit_years[2].summary_editable = False
        self.learning_unit_years[2].save()

        url = reverse(list_my_attributions_summary_editable)
        response = self.client.get(url)
        self.assertTemplateUsed(response, "manage_my_courses/list_my_courses_summary_editable.html")

        context = response.context[-1]
        self.assertCountEqual(context['learning_unit_years_summary_editable'],
                              [self.learning_unit_years[1], self.learning_unit_years[3]])

    def test_list_my_attributions_summary_responsible_false_for_some(self):
        self.client.force_login(self.user)

        self.attributions[0].summary_responsible = False
        self.attributions[0].save()
        self.attributions[2].summary_responsible = False
        self.attributions[2].save()

        url = reverse(list_my_attributions_summary_editable)
        response = self.client.get(url)
        self.assertTemplateUsed(response, "manage_my_courses/list_my_courses_summary_editable.html")

        context = response.context[-1]
        self.assertCountEqual(context['learning_unit_years_summary_editable'],
                              [self.learning_unit_years[1], self.learning_unit_years[3]])

    def test_list_my_attributions_summary_responsible_and_summary_editable_false_for_some(self):
        self.client.force_login(self.user)

        self.attributions[0].summary_responsible = False
        self.attributions[0].save()
        self.attributions[2].summary_responsible = False
        self.attributions[2].save()

        self.attributions[0].summary_responsible = False
        self.attributions[0].save()
        self.attributions[2].summary_responsible = False
        self.attributions[2].save()

        url = reverse(list_my_attributions_summary_editable)
        response = self.client.get(url)
        self.assertTemplateUsed(response, "manage_my_courses/list_my_courses_summary_editable.html")

        context = response.context[-1]
        self.assertCountEqual(context['learning_unit_years_summary_editable'],
                              [self.learning_unit_years[1], self.learning_unit_years[3]])
