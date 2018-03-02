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
from django.urls import reverse

from attribution.tests.factories.attribution import AttributionFactory
from base.forms.learning_unit_pedagogy import LearningUnitPedagogyForm
from base.models.tutor import Tutor
from base.tests.factories.person import PersonFactory
from base.tests.factories.tutor import TutorFactory


class ManageMyCoursesViewTestCase(TestCase):
    def setUp(self):
        self.person = PersonFactory()
        self.user = self.person.user
        self.tutor = TutorFactory(person=self.person)

    def test_list_my_attributions_user_not_logged(self):
        url = reverse("list_my_attributions")
        self.client.logout()
        response = self.client.get(url)
        self.assertRedirects(response, '/login/?next={}'.format(url))

    def test_list_my_attributions_user_not_tutor(self):
        tutors = Tutor.objects.filter(person__user=self.user)
        tutors.delete()

        self.client.force_login(self.user)
        url = reverse("list_my_attributions")
        response = self.client.get(url, follow=True)
        self.assertRedirects(response, '/login/?next={}'.format(url))

    def test_list_my_attributions(self):
        self.client.force_login(self.user)
        url = reverse("list_my_attributions")
        response = self.client.get(url)
        self.assertTemplateUsed(response, "manage_my_courses/list_my_attributions.html")


class TestEditEducationalInformation(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.tutor = TutorFactory()
        cls.attribution = AttributionFactory(tutor=cls.tutor, summary_responsible=True)
        cls.url = reverse("manage_educational_information", args=[cls.attribution.id])

    def setUp(self):
        self.client.force_login(self.tutor.person.user)

    def test_user_not_logged(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, '/login/?next={}'.format(self.url))

    def test_template_used(self):
        response = self.client.get(self.url)

        self.assertTemplateUsed(response, "manage_my_courses/educational_information.html")

        context = response.context
        self.assertEqual(context["learning_unit_year"], self.attribution.learning_unit_year)
        self.assertTrue(context["cms_labels_translated"])
        self.assertIsInstance(context["form_french"], LearningUnitPedagogyForm)
        self.assertIsInstance(context["form_english"], LearningUnitPedagogyForm)

