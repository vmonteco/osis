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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
import datetime

from django.core.urlresolvers import reverse
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseNotFound
from django.test import TestCase

from attribution.tests.factories.attribution import AttributionFactory
from base.models.learning_unit import LearningUnit
from base.tests.factories.person import PersonFactory
from base.tests.factories.tutor import TutorFactory
from base.models.enums import academic_calendar_type
from base.tests.factories.academic_calendar import AcademicCalendarFactory
from base.tests.factories.academic_year import AcademicYearFakerFactory
from django.utils import timezone
from base.tests.factories.learning_unit_year import LearningUnitYearFakerFactory
from base.forms.learning_unit_summary import LearningUnitSummaryForm
from cms.enums import entity_name
from cms.tests.factories.text_label import TextLabelFactory
from cms.tests.factories.translated_text import TranslatedTextFactory
from reference.tests.factories.language import LanguageFactory


class TestLearningUnitSummary(TestCase):
    def setUp(self):
        self.tutor = TutorFactory()

        self.learning_unit_year = LearningUnitYearFakerFactory()
        self.attribution = AttributionFactory(learning_unit_year=self.learning_unit_year, summary_responsible=True,
                                              tutor=self.tutor)

        self.url = reverse('learning_unit_summary', args=[self.learning_unit_year.id])
        self.client.force_login(self.tutor.person.user)

    def test_user_is_not_logged(self):
        self.client.logout()
        response = self.client.get(self.url)

        self.assertRedirects(response, "/login/?next={}".format(self.url))

    def test_user_is_not_a_tutor(self):
        self.person = PersonFactory()
        self.client.force_login(self.person.user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, HttpResponseForbidden.status_code)
        self.assertTemplateUsed(response, 'access_denied.html')

    def test_when_learning_unit_year_does_not_exist(self):
        self.learning_unit_year.delete()
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, HttpResponseNotFound.status_code)
        self.assertTemplateUsed(response, 'page_not_found.html')


    def test_when_user_is_not_attributed_to_the_learning_unit(self):
        self.attribution.delete()
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, HttpResponseNotFound.status_code)
        self.assertTemplateUsed(response, 'page_not_found.html')

    def test_when_user_is_not_summary_responsible_of_the_learning_unit(self):
        self.attribution.summary_responsible = False
        self.attribution.save()
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, HttpResponseForbidden.status_code)
        self.assertTemplateUsed(response, 'access_denied.html')

    def test_when_valid_get_request(self):
        response = self.client.get(self.url)

        self.assertTemplateUsed(response, "my_osis/educational_information.html")

        context = response.context
        self.assertEqual(context["learning_unit_year"], self.learning_unit_year)
        self.assertTrue(context["form_french"])
        self.assertTrue(context["form_english"])
        self.assertTrue(context["cms_labels_translated"])

