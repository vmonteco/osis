##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2017 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.test import TestCase, RequestFactory

from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.person import PersonFactory

from assistant.views.phd_supervisor_review import generate_phd_supervisor_menu_tabs
from assistant.tests.factories.review import ReviewFactory
from assistant.tests.factories.assistant_mandate import AssistantMandateFactory
from assistant.tests.factories.academic_assistant import AcademicAssistantFactory
from assistant.models.enums import assistant_mandate_state, review_status


class PhdSupervisorReviewViewTestCase(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        today = datetime.date.today()
        self.current_academic_year = AcademicYearFactory(start_date=today,
                                                         end_date=today.replace(year=today.year + 1),
                                                         year=today.year)
        self.phd_supervisor = PersonFactory()
        self.assistant = AcademicAssistantFactory(supervisor=self.phd_supervisor)
        self.assistant_mandate = AssistantMandateFactory(academic_year=self.current_academic_year,
                                                         assistant=self.assistant)
        self.assistant_mandate.state = assistant_mandate_state.PHD_SUPERVISOR
        self.assistant_mandate.save()
        self.review = ReviewFactory(reviewer=None, mandate=self.assistant_mandate,
                                    status=review_status.IN_PROGRESS)

    def test_generate_phd_supervisor_menu_tabs(self):
        self.client.force_login(self.phd_supervisor)
        # Review has not been completed -> supervisor can edit
        self.assertEqual(generate_phd_supervisor_menu_tabs(self.assistant_mandate, None),
                         [{'item': assistant_mandate_state.PHD_SUPERVISOR, 'class': '',
                          'action': 'edit'}])
        self.assertEqual(generate_phd_supervisor_menu_tabs(self.assistant_mandate,
                                                           assistant_mandate_state.PHD_SUPERVISOR),
                         [{'item': assistant_mandate_state.PHD_SUPERVISOR, 'class': 'active',
                           'action': 'edit'}])
        # Review has been completed -> supervisor can only view his review
        self.review.status = review_status.DONE
        self.review.save()
        self.assistant_mandate.state = assistant_mandate_state.RESEARCH
        self.assistant_mandate.save()
        self.assertEqual(generate_phd_supervisor_menu_tabs(self.assistant_mandate, None),
                         [{'item': assistant_mandate_state.PHD_SUPERVISOR, 'class': '',
                           'action': 'view'}])
        self.assertEqual(generate_phd_supervisor_menu_tabs(self.assistant_mandate,
                                                           assistant_mandate_state.PHD_SUPERVISOR),
                         [{'item': assistant_mandate_state.PHD_SUPERVISOR, 'class': 'active',
                           'action': 'view'}])

