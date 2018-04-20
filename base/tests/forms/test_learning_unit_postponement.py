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
from unittest import mock
import factory
import factory.fuzzy

from django.forms import model_to_dict
from django.http import QueryDict

from base.forms.learning_unit.learning_unit_create_2 import PartimForm, FullForm
from base.forms.learning_unit.learning_unit_postponement import LearningUnitPostponementForm
from base.forms.utils import acronym_field
from base.models.learning_unit import LearningUnit
from base.models.learning_unit_year import LearningUnitYear
from base.tests.factories.business.learning_units import GenerateContainer, GenerateAcademicYear
from base.tests.factories.learning_unit import LearningUnitFactory

from django.test import TestCase

from base.forms.learning_unit.learning_unit_create import LearningUnitYearModelForm, \
    LearningUnitModelForm, EntityContainerFormset, LearningContainerYearModelForm, LearningContainerModelForm
from base.models.enums import learning_unit_year_subtypes
from base.tests.factories.academic_year import create_current_academic_year
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.person import PersonFactory

FULL_ACRONYM = 'LAGRO1000'
SUBDIVISION_ACRONYM = 'C'


class LearningUnitPostponementFormContextMixin(TestCase):
    """This mixin is used in this test file in order to setup an environment for testing LEARNING UNIT POSTPONEMENT
       FORM"""
    def setUp(self):
        self.person = PersonFactory()
        self.current_academic_year = create_current_academic_year()
        self.generated_ac_years = GenerateAcademicYear(self.current_academic_year.year + 1,
                                                       self.current_academic_year.year + 10)

        # Creation of a LearingContainerYear and all related models - FOR 6 years
        self.learn_unit_structure = GenerateContainer(self.current_academic_year.year,
                                                      self.current_academic_year.year + 6)
        # Build in Generated Container [first index = start Generate Container ]
        self.generated_container_year = self.learn_unit_structure.generated_container_years[0]

        # Update All full learning unit year acronym
        LearningUnitYear.objects.filter(learning_unit=self.learn_unit_structure.learning_unit_full)\
                                .update(acronym=FULL_ACRONYM)
        # Update All partim learning unit year acronym
        LearningUnitYear.objects.filter(learning_unit=self.learn_unit_structure.learning_unit_partim) \
                                .update(acronym=FULL_ACRONYM + SUBDIVISION_ACRONYM)


class TestLearningUnitPostponementFormInit(LearningUnitPostponementFormContextMixin):
    """Unit tests for LearningUnitPostponementForm.__init__()"""
    def setUp(self):
        super().setUp()
        self.learning_unit_year_full = LearningUnitYear.objects.get(
            learning_unit=self.learn_unit_structure.learning_unit_full,
            academic_year=self.current_academic_year
        )

    def test_wrong_instance_args(self):
        wrong_instance = LearningUnitFactory()
        with self.assertRaises(AttributeError):
            _instanciate_postponement_form(instance=wrong_instance, person=self.person)

    def test_forms_property_for_full_end_year_is_none(self):
        self.learn_unit_structure.learning_unit_full.end_year = None
        self.learn_unit_structure.learning_unit_full.save()
        instance_luy_base_form = _instanciate_base_learning_unit_form(self.learning_unit_year_full, self.person)
        form = _instanciate_postponement_form(instance_luy_base_form, self.person)

        self.assertIsInstance(form._forms_to_upsert, list)
        self.assertIsInstance(form._forms_to_delete, list)
        self.assertEqual(len(form._forms_to_upsert), 6)
        self.assertFalse(form._forms_to_delete)

    def test_forms_property_for_full_end_year_is_current_year(self):
        self.learn_unit_structure.learning_unit_full.end_year = self.current_academic_year.year
        self.learn_unit_structure.learning_unit_full.save()
        instance_luy_base_form = _instanciate_base_learning_unit_form(self.learning_unit_year_full, self.person)
        form = _instanciate_postponement_form(instance_luy_base_form, self.person)

        self.assertFalse(form._forms_to_upsert)
        #self.assertEqual(len(form._forms_to_delete), 6)


def _instanciate_base_learning_unit_form(learning_unit_year_instance, person):
    form = FullForm if learning_unit_year_instance.subtype == learning_unit_year_subtypes.FULL else PartimForm
    form_args = {
        'learning_unit_year_full': learning_unit_year_instance.parent,
        'instance': learning_unit_year_instance,
        'data': {},
        'person': person
    }
    return form(**form_args)


def _instanciate_postponement_form(instance, person):
    return LearningUnitPostponementForm(instance, person)