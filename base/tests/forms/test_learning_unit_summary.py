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
from django.test import TestCase
from reference.tests.factories.language import LanguageFactory
from base.forms.learning_unit_summary import LearningUnitSummaryEditForm
from cms.tests.factories.text_label import TextLabelFactory
from cms.tests.factories.translated_text import TranslatedTextFactory
from cms.enums import entity_name


class TestValidation(TestCase):
    def setUp(self):
        self.language = LanguageFactory(code="EN")
        self.form_data = {
            "trans_text": "Text",
            "cms_id": 1
        }

    def test_invalid_form(self):
        del self.form_data['cms_id']
        form = LearningUnitSummaryEditForm(self.form_data)
        self.assertFalse(form.is_valid())

    def test_valid_form(self):
        form = LearningUnitSummaryEditForm(self.form_data)
        self.assertEqual(form.errors, {})
        self.assertTrue(form.is_valid())

    def test_save_form(self):

        text_label_lu = TextLabelFactory(order=1, label='program 1', entity=entity_name.LEARNING_UNIT_YEAR)

        translated_text_lu = TranslatedTextFactory(text_label=text_label_lu,
                                                   entity=entity_name.LEARNING_UNIT_YEAR)

        new_text = "New text replace {}".format(translated_text_lu.text)

        form = LearningUnitSummaryEditForm({
            "trans_text": new_text,
            "cms_id": translated_text_lu.id
        })
        form.is_valid()
        form.save()
        translated_text_lu.refresh_from_db()

        self.assertEqual(translated_text_lu.text, new_text)
