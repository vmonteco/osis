############################################################################
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
############################################################################
from django import forms
from django.core.validators import RegexValidator
from django.test import TestCase

from base.forms.common import ValidationRuleMixin
from base.models.validation_rule import ValidationRule
from reference.models.continent import Continent


class TestForm(ValidationRuleMixin, forms.ModelForm):
    class Meta:
        model = Continent
        fields = "__all__"


class TestValidationRuleMixin(TestCase):
    def setUp(self):
        ValidationRule.objects.create(
            field_reference="reference_continent.name",
            required_field=False,
            disabled_field=True,
            initial_value="LalaLand",
        )
        ValidationRule.objects.create(
            field_reference="reference_continent.code",
            required_field=True,
            disabled_field=False,
            initial_value="LA",
            regex_rule="^(LA|LB)$"
        )

    def test_init(self):
        form = TestForm()
        self.assertFalse(form.fields["name"].required)
        self.assertTrue(form.fields["name"].disabled)
        self.assertEqual(form.fields["name"].initial, "LalaLand")

        self.assertTrue(form.fields["code"].required)
        self.assertFalse(form.fields["code"].disabled)
        self.assertEqual(form.fields["code"].initial, "LA")
        self.assertIsInstance(form.fields["code"].validators[1], RegexValidator)

    def test_is_valid(self):
        form = TestForm(
            data={
                'name': "Zoubiland",
                'code': 'LB'
            }
        )
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["name"], "LalaLand")
        self.assertEqual(form.cleaned_data["code"], "LB")

    def test_is_invalid(self):
        form = TestForm(
            data={
                'name': "Zoubiland",
                'code': 'LZ'
            }
        )
        self.assertFalse(form.is_valid())
