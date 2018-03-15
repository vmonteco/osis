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
import datetime

from django.forms import formset_factory
from django.test import RequestFactory, TestCase, Client

from assistant.models.enums import reviewer_role
from base.models import academic_year
from assistant.forms import ReviewersFormset
from base.models.entity import find_versions_from_entites
from base.models.enums import entity_type
from base.tests.factories.academic_year import AcademicYearFactory
from assistant.tests.factories.manager import ManagerFactory
from assistant.tests.factories.reviewer import ReviewerFactory
from assistant.views.reviewers_management import reviewer_delete
from assistant.models.reviewer import find_by_person
from base.tests.factories.entity import EntityFactory
from base.tests.factories.entity_version import EntityVersionFactory
from base.tests.factories.person import PersonFactory

HTTP_OK = 200

class ReviewersManagementViewTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.person2 = PersonFactory()
        self.manager = ManagerFactory()
        self.entity_factory = EntityFactory()
        self.entity_version = EntityVersionFactory(entity_type=entity_type.INSTITUTE,
                                                   end_date=None,
                                                   entity=self.entity_factory)
        self.reviewer = ReviewerFactory(role=reviewer_role.RESEARCH,
                                        entity=self.entity_version.entity)
        self.reviewer2 = ReviewerFactory()
        self.formset = formset_factory(ReviewersFormset)
        today = datetime.date.today()
        self.current_academic_year = AcademicYearFactory(start_date=today,
                                                         end_date=today.replace(year=today.year + 1),
                                                         year=today.year)

    def test_reviewer_delete(self):
        self.person = self.reviewer.person
        self.client.force_login(self.person.user)
        response = self.client.post('/assistants/manager/reviewers/action/', {'action': 'DELETE',
                                                                          'id': self.reviewer.id
                                                                          })

        self.assertFalse(find_by_person(self.person))
        self.assertTrue(find_by_person(self.reviewer2.person))
        self.assertEqual(response.status_code, HTTP_OK)

    def test_reviewer_add(self):
        self.person = self.manager.person
        self.client.force_login(self.person.user)
        this_entity = find_versions_from_entites([self.entity_factory.id], date=None) [0]
        response = self.client.post('/assistants/manager/reviewers/add/', {'entity': this_entity.id,
                                                                          'role': self.reviewer.role,
                                                                          'person_id': self.person2.id,
                                                                          })
        self.assertEqual(response.status_code, HTTP_OK)





