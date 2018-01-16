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

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseForbidden
from django.test import TestCase

from base.models.learning_unit import LearningUnit
from base.tests.factories.person import PersonFactory

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
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse, HttpResponseForbidden


class TestLearningUnitSummaryPermission(TestCase):

    def setUp(self):
        self.person = PersonFactory()
        self.client.force_login(self.person.user)
        self.learning_unit_year = LearningUnitYearFakerFactory()
        self.url = reverse('learning_unit_summary', args=[self.learning_unit_year.id])

    def test_forbidden(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HttpResponseForbidden.status_code)
        self.assertTemplateUsed(response, 'access_denied.html')

    def test_authorized(self):
        self.set_permission()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertTemplateUsed(response, 'learning_unit/summary.html')

    def set_permission(self):
        content_type = ContentType.objects.get_for_model(LearningUnit)
        permission = Permission.objects.get(codename="can_access_learningunit",
                                            content_type=content_type)
        self.person.user.user_permissions.add(permission)


class TestLearningUnitSummary(TestCase):
    def setUp(self):
        self.person = PersonFactory()
        content_type = ContentType.objects.get_for_model(LearningUnit)
        permission = Permission.objects.get(codename="can_access_learningunit",
                                            content_type=content_type)
        self.person.user.user_permissions.add(permission)
        self.client.force_login(self.person.user)

        current_academic_year = AcademicYearFakerFactory(start_date=timezone.now() - datetime.timedelta(days=10),
                                                         end_date=timezone.now() + datetime.timedelta(days=10))

        AcademicCalendarFactory(academic_year=current_academic_year,
                                reference=academic_calendar_type.SUMMARY_COURSE_SUBMISSION)

        self.language = LanguageFactory(code="en")
        self.learning_unit_year = LearningUnitYearFakerFactory()

        self.text_label_lu = TextLabelFactory(order=1,
                                              label=LearningUnitSummaryForm.RESUME,
                                              entity=entity_name.LEARNING_UNIT_YEAR)

        self.translated_text_lu = TranslatedTextFactory(text_label=self.text_label_lu,
                                                        entity=entity_name.LEARNING_UNIT_YEAR,
                                                        language=self.language,
                                                        reference=self.learning_unit_year.id)

        self.form_data = {
            "learning_unit_year": self.learning_unit_year.id,
            "language": self.language,
            "text_label": self.text_label_lu
        }
        self.url = reverse('learning_unit_summary_edit', args=[self.learning_unit_year.id])

    def test_learning_unit_summary_form(self):
        response = self.client.get(self.url, data={
            "learning_unit_year": self.learning_unit_year.id,
            "language": self.language,
            "label": LearningUnitSummaryForm.RESUME
        })

        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertTemplateUsed(response, 'learning_unit/summary_edit.html')
