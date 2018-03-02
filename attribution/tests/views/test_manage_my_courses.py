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
