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
from unittest import mock
from django.test import TestCase, RequestFactory, Client
from django.core.urlresolvers import reverse
from django.contrib import auth

from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.entity_version import EntityVersionFactory
from base.models.enums import entity_type
from base.tests.factories.entity import EntityFactory
from reference.tests.factories.country import CountryFactory


from assistant.views.phd_supervisor_review import generate_phd_supervisor_menu_tabs
from assistant.views.phd_supervisor_review import user_is_phd_supervisor_and_procedure_is_open
from assistant.tests.factories.review import ReviewFactory
from assistant.tests.factories.assistant_mandate import AssistantMandateFactory
from assistant.tests.factories.mandate_entity import MandateEntityFactory
from assistant.tests.factories.reviewer import ReviewerFactory
from assistant.tests.factories.academic_assistant import AcademicAssistantFactory
from assistant.tests.factories.settings import SettingsFactory
from assistant.models.enums import assistant_mandate_state, review_status, reviewer_role


class ReviewerReviewViewTestCase(TestCase):

    def setUp(self):

        self.factory = RequestFactory()
        self.client = Client()
        self.settings = SettingsFactory()
        today = datetime.date.today()
        self.current_academic_year = AcademicYearFactory(start_date=today,
                                                         end_date=today.replace(year=today.year + 1),
                                                         year=today.year)
        self.assistant = AcademicAssistantFactory()
        self.assistant_mandate = AssistantMandateFactory(academic_year=self.current_academic_year,
                                                         assistant=self.assistant,
                                                         state=assistant_mandate_state.RESEARCH)
        self.entity_version = EntityVersionFactory(entity_type=entity_type.INSTITUTE)
        self.entity = self.entity_version.entity
        self.entity_mandate = MandateEntityFactory(assistant_mandate=self.assistant_mandate,
                                                   entity=self.entity)
        self.reviewer = ReviewerFactory(role=reviewer_role.RESEARCH,
                                        entity=self.entity)
        self.review = ReviewFactory(reviewer=self.reviewer, mandate=self.assistant_mandate,
                                    status=review_status.IN_PROGRESS)

    def test_pst_form_view(self):
        self.client.force_login(self.reviewer.person.user)
        response = self.client.post('/assistants/reviewer/pst_form/', {'mandate_id': self.assistant_mandate.id})
        self.assertEqual(response.status_code, 200)

    def test_review_view(self):
        self.client.force_login(self.reviewer.person.user)
        response = self.client.post('/assistants/reviewer/review/view/', {'mandate_id': self.assistant_mandate.id})
        self.assertEqual(response.status_code, 200)

    def test_review_edit(self):
        self.client.force_login(self.reviewer.person.user)
        response = self.client.post('/assistants/reviewer/review/edit/', {'mandate_id': self.assistant_mandate.id})
        self.assertEqual(response.status_code, 200)
        self.review.status = review_status.DONE
        self.review.save()
        response = self.client.post('/assistants/reviewer/review/edit/',{'mandate_id': self.assistant_mandate.id})
        self.assertEqual(response.status_code, 302)

    def test_review_save(self):
        self.client.force_login(self.reviewer.person.user)
        response = self.client.post('/assistants/reviewer/review/save/', {'mandate_id': self.assistant_mandate.id,
                                                                          'review_id': self.review.id
                                                                          })
        self.assertEqual(response.status_code, 200)
