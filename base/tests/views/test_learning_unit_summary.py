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

from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.http import HttpResponseForbidden, HttpResponseNotFound
from django.test import TestCase

from attribution.tests.factories.attribution import AttributionFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.tutor import TutorFactory
from base.models.enums import academic_calendar_type
from base.tests.factories.academic_calendar import AcademicCalendarFactory
from base.tests.factories.academic_year import AcademicYearFakerFactory, create_current_academic_year
from base.tests.factories.learning_unit_year import LearningUnitYearFakerFactory
from base.tests.factories.learning_container_year import LearningContainerYearFactory
from cms.tests.factories.text_label import TextLabelFactory
from cms.tests.factories.translated_text import TranslatedTextFactory
from cms.tests.factories.translated_text_label import TranslatedTextLabelFactory


class TestLearningUnitSummary(TestCase):
    @classmethod
    def setUpTestData(cls):
        academic_year = create_current_academic_year()
        cls.summary_course_submission_calendar = AcademicCalendarFactory(
            academic_year=academic_year,
            start_date=academic_year.start_date,
            end_date=academic_year.end_date,
            reference=academic_calendar_type.SUMMARY_COURSE_SUBMISSION)

        cls.tutor = TutorFactory()

        cls.learning_unit_year = LearningUnitYearFakerFactory(academic_year=academic_year)
        cls.attribution = AttributionFactory(learning_unit_year=cls.learning_unit_year, summary_responsible=True,
                                             tutor=cls.tutor)

        cls.url = reverse('learning_unit_summary', args=[cls.learning_unit_year.id])

    def setUp(self):
        self.client.force_login(self.tutor.person.user)

    def test_user_is_not_logged(self):
        self.client.logout()
        response = self.client.get(self.url)

        self.assertRedirects(response, "/login/?next={}".format(self.url))

    def test_summary_course_submission_calendar_is_not_opened(self):
        today = datetime.date.today()
        self.summary_course_submission_calendar.start_date = today-datetime.timedelta(days=5)
        self.summary_course_submission_calendar.end_date = today - datetime.timedelta(days=3)
        self.summary_course_submission_calendar.save()
        response = self.client.get(self.url)

        self.assertRedirects(response, reverse("outside_summary_submission_period"))

    def test_summary_course_submission_calendar_is_not_set(self):
        self.summary_course_submission_calendar.delete()
        response = self.client.get(self.url)

        self.assertRedirects(response, reverse("outside_summary_submission_period"))

    def test_user_is_not_a_tutor(self):
        person = PersonFactory()
        self.client.force_login(person.user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, HttpResponseForbidden.status_code)
        self.assertTemplateUsed(response, 'access_denied.html')

    def test_when_user_is_not_attributed_to_the_learning_unit(self):
        self.attribution.delete()
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, HttpResponseForbidden.status_code)
        self.assertTemplateUsed(response, 'access_denied.html')

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


class TestLearningUnitSummaryEdit(TestCase):
    def setUp(self):
        today = datetime.date.today()
        academic_year = AcademicYearFakerFactory(start_date=today-datetime.timedelta(days=3), year=today.year,
                                                 end_date=today + datetime.timedelta(days=5))
        self.summary_course_submission_calendar = \
            AcademicCalendarFactory(academic_year=academic_year,
                                    start_date=academic_year.start_date,
                                    end_date=academic_year.end_date,
                                    reference=academic_calendar_type.SUMMARY_COURSE_SUBMISSION)

        self.tutor = TutorFactory()

        learning_container_year = LearningContainerYearFactory(academic_year=academic_year)
        self.learning_unit_year = LearningUnitYearFakerFactory(academic_year=academic_year,
                                                               learning_container_year=learning_container_year)
        self.attribution = AttributionFactory(learning_unit_year=self.learning_unit_year, summary_responsible=True,
                                              tutor=self.tutor)

        self.url = reverse('learning_unit_summary_edit', args=[self.learning_unit_year.id])
        self.client.force_login(self.tutor.person.user)

    def test_user_is_not_logged(self):
        self.client.logout()
        response = self.client.get(self.url)

        self.assertRedirects(response, "/login/?next={}".format(self.url))

    def test_summary_course_submission_calendar_is_not_opened(self):
        today = datetime.date.today()
        self.summary_course_submission_calendar.start_date = today-datetime.timedelta(days=5)
        self.summary_course_submission_calendar.end_date = today - datetime.timedelta(days=3)
        self.summary_course_submission_calendar.save()
        response = self.client.get(self.url)

        self.assertRedirects(response, reverse("outside_summary_submission_period"))

    def test_summary_course_submission_calendar_is_not_set(self):
        self.summary_course_submission_calendar.delete()
        response = self.client.get(self.url)

        self.assertRedirects(response, reverse("outside_summary_submission_period"))

    def test_user_is_not_a_tutor(self):
        person = PersonFactory()
        self.client.force_login(person.user)

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

        self.assertEqual(response.status_code, HttpResponseForbidden.status_code)
        self.assertTemplateUsed(response, 'access_denied.html')

    def test_when_user_is_not_summary_responsible_of_the_learning_unit(self):
        self.attribution.summary_responsible = False
        self.attribution.save()
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, HttpResponseForbidden.status_code)
        self.assertTemplateUsed(response, 'access_denied.html')

    def test_valid_get_request(self):
        language = "en"
        text_label = TextLabelFactory()
        response = self.client.get(self.url, data={"language": language, "label": text_label.label})

        self.assertTemplateUsed(response, "my_osis/educational_information_edit.html")

        context = response.context
        self.assertEqual(context["learning_unit_year"], self.learning_unit_year)
        self.assertTrue(context["form"])
        self.assertEqual(context["text_label_translated"], None)
        self.assertEqual(context["language_translated"], ('en', _('English')))

    def test_valid_get_request_with_translated_text_labels(self):
        language = "fr-be"
        self.tutor.person.language = language
        self.tutor.person.save()
        trans_text_label = TranslatedTextLabelFactory()
        response = self.client.get(self.url, data={"language": language, "label": trans_text_label.text_label.label})

        self.assertTemplateUsed(response, "my_osis/educational_information_edit.html")

        context = response.context
        self.assertEqual(context["learning_unit_year"], self.learning_unit_year)
        self.assertTrue(context["form"])
        self.assertEqual(context["text_label_translated"], trans_text_label)
        self.assertEqual(context["language_translated"], ('fr-be', _('French')))

    def test_invalid_post_request(self):
        response = self.client.post(self.url, data={"trans_text": "Hello world!!"})
        self.assertRedirects(response, reverse("learning_unit_summary", args=[self.learning_unit_year.id]))

    def test_valid_post_request(self):
        new_text = "Hello world!!"
        translated_text = TranslatedTextFactory()
        response = self.client.post(self.url, data={"trans_text": new_text, "cms_id": translated_text.id})

        self.assertRedirects(response, reverse("learning_unit_summary", args=[self.learning_unit_year.id]))
        translated_text.refresh_from_db()
        self.assertEqual(translated_text.text, new_text)
