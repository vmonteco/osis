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

from django.test import TestCase

from assistant.views.mandate import get_reviews
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.person import PersonFactory

from assistant.models.enums import assistant_mandate_state
from assistant.forms import MandateForm
from assistant.tests.factories.academic_assistant import AcademicAssistantFactory
from assistant.tests.factories.assistant_mandate import AssistantMandateFactory
from assistant.tests.factories.manager import ManagerFactory


HTTP_OK = 200
HTTP_FOUND = 302

class MandateViewTestCase(TestCase):
    def setUp(self):
        self.current_academic_year = AcademicYearFactory()
        self.manager = ManagerFactory()
        self.person = PersonFactory()
        self.assistant = AcademicAssistantFactory()
        self.assistant_mandate = AssistantMandateFactory()
        self.assistant_mandate2 = AssistantMandateFactory(academic_year=self.current_academic_year,
                                                         assistant= self.assistant,
                                                         state=assistant_mandate_state.PHD_SUPERVISOR)


    def test_mandate_edit(self):
        self.client.force_login(self.manager.person.user)
        response = self.client.post("/assistants/manager/mandates/edit/" , {'mandate_id': self.assistant_mandate.id})
        self.assertEqual(response.status_code, HTTP_OK)


    #def test_mandate_save(self):
    #    self.client.force_login(self.manager.person.user)
    #    form = MandateForm(data={'contract_duration': self.assistant_mandate2.contract_duration,
    #                             'contract_duration_fte': self.assistant_mandate2.contract_duration_fte,
    #                             'sap_id': self.assistant_mandate2.sap_id})
    #    response = self.client.post("/assistants/manager/mandates/save/" , {'mandate_id': self.assistant_mandate2.id,
    #                                                                        form: form})
    #    self.assertEqual(response.status_code, HTTP_OK)
    def test_get_reviews(self):
        self.client.force_login(self.manager.person.user)
        self.assertEqual(get_reviews(self.assistant_mandate), [])


