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
from django.forms import formset_factory
from django.test import RequestFactory, TestCase, Client

from assistant.forms import ReviewersFormset
from assistant.tests.factories.manager import ManagerFactory
from assistant.tests.factories.reviewer import ReviewerFactory
from assistant.views.reviewers_management import reviewer_delete
from assistant.models.reviewer import find_by_person

HTTP_OK = 200

class ReviewersManagementViewTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.manager = ManagerFactory()
        self.reviewer = ReviewerFactory()
        self.reviewer2 = ReviewerFactory()
        self.formset = formset_factory(ReviewersFormset)

    def test_reviewer_delete(self):
        self.person = self.reviewer.person
        self.client.force_login(self.person.user)
        response = self.client.post('/assistants/manager/reviewers/action/', {'action': 'DELETE',
                                                                          'id': self.reviewer.id
                                                                          })

        self.assertFalse(find_by_person(self.person))
        self.assertTrue(find_by_person(self.reviewer2.person))
        #self.assertEqual(response.status_code, HTTP_OK)



