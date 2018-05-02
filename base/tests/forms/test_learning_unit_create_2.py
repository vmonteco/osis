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
from unittest import mock

from django.test import TestCase

from base.forms.learning_unit.learning_unit_create import LearningUnitYearModelForm, \
    LearningUnitModelForm, EntityContainerFormset, LearningContainerYearModelForm, LearningContainerModelForm
from base.forms.learning_unit.learning_unit_create_2 import FullForm, FULL_READ_ONLY_FIELDS, \
    FULL_PROPOSAL_READ_ONLY_FIELDS
from base.models.academic_year import AcademicYear
from base.models.entity_component_year import EntityComponentYear
from base.models.entity_container_year import EntityContainerYear
from base.models.enums import learning_unit_year_subtypes, learning_container_year_types, organization_type
from base.models.learning_component_year import LearningComponentYear
from base.models.learning_container import LearningContainer
from base.models.learning_container_year import LearningContainerYear
from base.models.learning_unit import LearningUnit
from base.models.learning_unit_component import LearningUnitComponent
from base.models.learning_unit_year import LearningUnitYear
from base.tests.factories.academic_year import create_current_academic_year, AcademicYearFactory
from base.tests.factories.business.entities import create_entities_hierarchy
from base.tests.factories.business.learning_units import GenerateContainer, GenerateAcademicYear
from base.tests.factories.campus import CampusFactory
from base.tests.factories.entity_version import EntityVersionFactory
from base.tests.factories.learning_container_year import LearningContainerYearFactory
from base.tests.factories.learning_unit import LearningUnitFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.organization import OrganizationFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.person_entity import PersonEntityFactory
from reference.tests.factories.language import LanguageFactory


def _instanciate_form(academic_year, person=None, post_data=None, learning_unit_instance=None, start_year=None):
    if not person:
        person = PersonFactory()
    return FullForm(person, academic_year, learning_unit_instance=learning_unit_instance, data=post_data,
                    start_year=start_year)


def get_valid_form_data(academic_year, person, learning_unit_year=None):
    entities = create_entities_hierarchy()
    PersonEntityFactory(person=person, entity=entities['root_entity'], with_child=True)
    requirement_entity_version = entities['child_one_entity_version']
    organization = OrganizationFactory(type=organization_type.MAIN)
    campus = CampusFactory(organization=organization)

    if not learning_unit_year:

        container_year = LearningContainerYearFactory(academic_year=academic_year, campus=campus)
        learning_unit_year = LearningUnitYearFactory.build(academic_year=academic_year,
                                                           learning_container_year=container_year,
                                                           subtype=learning_unit_year_subtypes.FULL)
    return {
        # Learning unit year data model form
        'acronym': learning_unit_year.acronym,
        'acronym_0': learning_unit_year.acronym[0],
        'acronym_1': learning_unit_year.acronym[1:],
        'subtype': learning_unit_year.subtype,
        'academic_year': learning_unit_year.academic_year.id,
        'specific_title': learning_unit_year.specific_title,
        'specific_title_english': learning_unit_year.specific_title_english,
        'credits': learning_unit_year.credits,
        'session': learning_unit_year.session,
        'quadrimester': learning_unit_year.quadrimester,
        'status': learning_unit_year.status,
        'internship_subtype': learning_unit_year.internship_subtype,
        'attribution_procedure': learning_unit_year.attribution_procedure,

        # Learning unit data model form
        'periodicity': learning_unit_year.learning_unit.periodicity,
        'faculty_remark': learning_unit_year.learning_unit.faculty_remark,
        'other_remark': learning_unit_year.learning_unit.other_remark,

        # Learning container year data model form
        'campus': learning_unit_year.learning_container_year.campus.id,
        'language': learning_unit_year.learning_container_year.language.id,
        'common_title': learning_unit_year.learning_container_year.common_title,
        'common_title_english': learning_unit_year.learning_container_year.common_title_english,
        'container_type': learning_unit_year.learning_container_year.container_type,
        'type_declaration_vacant': learning_unit_year.learning_container_year.type_declaration_vacant,
        'team': learning_unit_year.learning_container_year.team,
        'is_vacant': learning_unit_year.learning_container_year.is_vacant,

        'entitycontaineryear_set-0-entity': requirement_entity_version.id,
        'entitycontaineryear_set-1-entity': requirement_entity_version.id,
        'entitycontaineryear_set-2-entity': '',
        'entitycontaineryear_set-INITIAL_FORMS': '0',
        'entitycontaineryear_set-MAX_NUM_FORMS': '4',
        'entitycontaineryear_set-MIN_NUM_FORMS': '3',
        'entitycontaineryear_set-TOTAL_FORMS': '4',
    }


class LearningUnitFullFormContextMixin(TestCase):
    """This mixin is used in this test file in order to setup an environment for testing FULL FORM"""
    def setUp(self):
        self.initial_language = LanguageFactory(code='FR')
        self.initial_campus = CampusFactory(name='Louvain-la-Neuve', organization__type=organization_type.MAIN)
        self.current_academic_year = create_current_academic_year()
        self.person = PersonFactory()
        self.post_data = get_valid_form_data(self.current_academic_year, person=self.person)
        # Creation of a LearingContainerYear and all related models
        self.learn_unit_structure = GenerateContainer(self.current_academic_year.year, self.current_academic_year.year)
        self.learning_unit_year = LearningUnitYear.objects.get(
            learning_unit=self.learn_unit_structure.learning_unit_full,
            academic_year=self.current_academic_year
        )

        acs = GenerateAcademicYear(
            start_year=self.current_academic_year.year+1, end_year=self.current_academic_year.year+7).academic_years
        for ac in acs:
            LearningUnitYearFactory(academic_year=ac, learning_unit=self.learning_unit_year.learning_unit)


class TestFullFormInit(LearningUnitFullFormContextMixin):
    """Unit tests for FullForm.__init__()"""

    def test_case_start_year_and_learning_unit_instance_kwarg_are_missing(self):
        with self.assertRaises(AttributeError):
            FullForm(self.person, self.learning_unit_year.academic_year, post_data=self.post_data)

    def test_disable_fields_full(self):
        form = FullForm(self.person, self.learning_unit_year.academic_year,
                        learning_unit_instance=self.learning_unit_year.learning_unit)
        disabled_fields = {key for key, value in form.fields.items() if value.disabled == True}
        self.assertEqual(disabled_fields, FULL_READ_ONLY_FIELDS)

    def test_disable_fields_full_proposal(self):
        form = FullForm(self.person, self.learning_unit_year.academic_year,
                        learning_unit_instance=self.learning_unit_year.learning_unit, proposal=True)
        disabled_fields = {key for key, value in form.fields.items() if value.disabled is True}
        self.assertEqual(disabled_fields, FULL_PROPOSAL_READ_ONLY_FIELDS)

    def test_subtype_is_full(self):
        learn_unit_year = LearningUnitYearFactory()
        form = _instanciate_form(learn_unit_year.academic_year, learning_unit_instance=learn_unit_year.learning_unit)
        self.assertEqual(form.subtype, learning_unit_year_subtypes.FULL)

    def test_wrong_instance_arg(self):
        wrong_instance = PersonFactory()
        with self.assertRaises(ValueError):
            _instanciate_form(AcademicYearFactory(year=1980), learning_unit_instance=wrong_instance)

    def test_model_forms_case_creation(self):
        form_classes_expected = [LearningUnitModelForm, LearningUnitYearModelForm, LearningContainerModelForm,
                                 LearningContainerYearModelForm, EntityContainerFormset]
        form = _instanciate_form(self.current_academic_year, post_data=self.post_data,
                                 start_year=self.current_academic_year.year)
        for cls in form_classes_expected:
            self.assertIsInstance(form.forms[cls], cls)

    def test_initial_values_of_forms_case_creation(self):
        full_form = _instanciate_form(self.current_academic_year, post_data=self.post_data,
                                      start_year=self.current_academic_year.year)
        expected_initials = {
            LearningUnitYearModelForm: {
                'status': True, 'academic_year': self.current_academic_year
            },
            LearningContainerYearModelForm: {
                'campus': self.initial_campus,
                'language': self.initial_language,
            }
        }
        for form_class, initial in expected_initials.items():
            self.assertEqual(full_form.forms[form_class].initial, initial)

    def test_model_forms_case_update(self):
        learn_unit_year = self.learning_unit_year
        form = _instanciate_form(self.learning_unit_year.academic_year,
                                 post_data=self.post_data, person=self.person,
                                 learning_unit_instance=learn_unit_year.learning_unit)

        self.assertEqual(form.forms[LearningUnitModelForm].instance, learn_unit_year.learning_unit)
        self.assertEqual(form.forms[LearningContainerModelForm].instance, learn_unit_year.learning_container_year.learning_container)
        self.assertEqual(form.forms[LearningUnitYearModelForm].instance, learn_unit_year)
        self.assertEqual(form.forms[LearningContainerYearModelForm].instance, learn_unit_year.learning_container_year)
        formset_instance = form.forms[EntityContainerFormset]
        self.assertEqual(formset_instance.forms[0].instance.learning_container_year, learn_unit_year.learning_container_year)
        self.assertEqual(formset_instance.forms[1].instance.learning_container_year, learn_unit_year.learning_container_year)


class TestFullFormIsValid(LearningUnitFullFormContextMixin):
    """Unit tests for is_valid() """

    def _assert_equal_values(self, obj, dictionnary, fields_to_validate):
        for field in fields_to_validate:
            self.assertEqual(getattr(obj, field), dictionnary[field], msg='Error field = {}'.format(field))

    def test_creation_case_correct_post_data(self):
        form = _instanciate_form(self.current_academic_year, post_data=self.post_data,
                                 start_year=self.current_academic_year.year)
        form.is_valid()
        self._test_learning_unit_model_form_instance(form)
        self._test_learning_unit_year_model_form_instance(form)
        self._test_learning_container_model_form_instance(form)
        self._test_learning_container_year_model_form_instance(form)

    def _test_learning_unit_model_form_instance(self, full_form):
        form_instance = full_form.forms[LearningUnitModelForm]
        fields_to_validate = ['faculty_remark', 'other_remark', 'periodicity']
        self._assert_equal_values(form_instance.instance, self.post_data, fields_to_validate)

    def _test_learning_container_model_form_instance(self, full_form):
        self.assertIn(LearningContainerModelForm, full_form.forms)

    def _test_learning_unit_year_model_form_instance(self, full_form):
        form_instance = full_form.forms[LearningUnitYearModelForm]
        fields_to_validate = ['acronym', 'specific_title', 'specific_title_english', 'credits',
                              'session', 'quadrimester', 'status', 'internship_subtype', 'attribution_procedure', 'subtype',]
        self._assert_equal_values(form_instance.instance, self.post_data, fields_to_validate)
        self.assertEqual(form_instance.instance.academic_year.id, self.post_data['academic_year'])

    def _test_learning_container_year_model_form_instance(self, full_form):
        form_instance = full_form.forms[LearningContainerYearModelForm]
        fields_to_validate = ['container_type', 'common_title', 'common_title_english',
                              'type_declaration_vacant', 'team', 'is_vacant']
        self._assert_equal_values(form_instance.instance, self.post_data, fields_to_validate)

    def _test_entity_container_model_formset_instance(self, full_form):
        self.assertIn(EntityContainerFormset, full_form.forms)

    @mock.patch('base.forms.learning_unit.learning_unit_create.LearningUnitModelForm.is_valid', side_effect=lambda *args: False)
    def test_creation_case_wrong_learning_unit_data(self, mock_is_valid):
        form = _instanciate_form(self.current_academic_year, post_data=self.post_data, start_year=self.current_academic_year.year)
        self.assertFalse(form.is_valid())

    @mock.patch('base.forms.learning_unit.learning_unit_create.LearningUnitYearModelForm.is_valid', side_effect=lambda *args: False)
    def test_creation_case_wrong_learning_unit_year_data(self, mock_is_valid):
        form = _instanciate_form(self.current_academic_year, post_data=self.post_data, start_year=self.current_academic_year.year)
        self.assertFalse(form.is_valid())

    @mock.patch('base.forms.learning_unit.learning_unit_create.LearningContainerYearModelForm.is_valid', side_effect=lambda *args: False)
    def test_creation_case_wrong_learning_container_year_data(self, mock_is_valid):
        form = _instanciate_form(self.current_academic_year, post_data=self.post_data, start_year=self.current_academic_year.year)
        self.assertFalse(form.is_valid())

    @mock.patch('base.forms.learning_unit.learning_unit_create.EntityContainerYearModelForm.is_valid', side_effect=lambda *args: False)
    def test_creation_case_wrong_entity_container_year_data(self, mock_is_valid):
        form = _instanciate_form(self.current_academic_year, post_data=self.post_data, start_year=self.current_academic_year.year)
        self.assertFalse(form.is_valid())

    @mock.patch('base.forms.learning_unit.learning_unit_create_2.FullForm._validate_same_entities_container', side_effect=lambda *args: False)
    def test_creation_case_not_same_entities_container(self, mock_is_valid):
        form = _instanciate_form(self.current_academic_year, post_data=self.post_data, start_year=self.current_academic_year.year)
        self.assertFalse(form.is_valid())

    @mock.patch('base.forms.learning_unit.learning_unit_create_2.FullForm._validate_no_empty_title', side_effect=lambda *args: False)
    def test_creation_case_wrong_titles(self, mock_is_valid):
        form = _instanciate_form(self.current_academic_year, post_data=self.post_data, start_year=self.current_academic_year.year)
        self.assertFalse(form.is_valid())

    def test_update_case_correct_data(self):
        now = datetime.datetime.now()
        learn_unit_structure = GenerateContainer(now.year, now.year)
        learn_unit_year = LearningUnitYear.objects.get(learning_unit=learn_unit_structure.learning_unit_full,
                                                       academic_year=AcademicYear.objects.get(year=now.year))
        form = _instanciate_form(learn_unit_year.academic_year, post_data=self.post_data, person=self.person,
                                 learning_unit_instance=learn_unit_year.learning_unit)
        self.assertTrue(form.is_valid(), form.errors)

    @mock.patch('base.forms.learning_unit.learning_unit_create.LearningUnitModelForm.is_valid', side_effect=lambda *args: False)
    def test_update_case_wrong_learning_unit_data(self, mock_is_valid):
        form = _instanciate_form(self.learning_unit_year.academic_year, post_data=self.post_data,
                                 learning_unit_instance=self.learning_unit_year.learning_unit)
        self.assertFalse(form.is_valid())

    @mock.patch('base.forms.learning_unit.learning_unit_create.LearningUnitYearModelForm.is_valid', side_effect=lambda *args: False)
    def test_update_case_wrong_learning_unit_year_data(self, mock_is_valid):
        form = _instanciate_form(self.learning_unit_year.academic_year, post_data=self.post_data,
                                 learning_unit_instance=self.learning_unit_year.learning_unit)
        self.assertFalse(form.is_valid())

    @mock.patch('base.forms.learning_unit.learning_unit_create.LearningContainerYearModelForm.is_valid', side_effect=lambda *args: False)
    def test_update_case_wrong_learning_container_year_data(self, mock_is_valid):
        form = _instanciate_form(self.learning_unit_year.academic_year, post_data=self.post_data,
                                 learning_unit_instance=self.learning_unit_year.learning_unit)
        self.assertFalse(form.is_valid())

    @mock.patch('base.forms.learning_unit.learning_unit_create.EntityContainerYearModelForm.is_valid', side_effect=lambda *args: False)
    def test_update_case_wrong_entity_container_year_data(self, mock_is_valid):
        form = _instanciate_form(self.learning_unit_year.academic_year, post_data=self.post_data, person=self.person,
                                 learning_unit_instance=self.learning_unit_year.learning_unit)
        self.assertFalse(form.is_valid())


class TestFullFormSave(LearningUnitFullFormContextMixin):
    """Unit tests for save() """
    def test_when_update_instance(self):
        self.post_data['credits'] = 99
        form = _instanciate_form(self.learning_unit_year.academic_year, post_data=self.post_data, person=self.person,
                                 learning_unit_instance=self.learning_unit_year.learning_unit)
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        self.assertEqual(LearningUnitYear.objects.get(pk=self.learning_unit_year.id).credits, 99)

    def test_when_create_instance(self):
        acronym = 'LAGRO1200'
        new_learning_unit_year = LearningUnitYearFactory.build(
            acronym=acronym,
            academic_year=self.current_academic_year,
            subtype=learning_unit_year_subtypes.FULL,
            learning_container_year__academic_year=self.current_academic_year,
            learning_container_year__container_type=learning_container_year_types.COURSE,
            learning_container_year__campus=self.initial_campus,
            learning_container_year__language=self.initial_language
        )
        post_data = get_valid_form_data(self.current_academic_year, person=self.person,
                                        learning_unit_year=new_learning_unit_year)
        form = _instanciate_form(self.current_academic_year, post_data=post_data, person=self.person,
                                 start_year=self.current_academic_year.year)
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        self.assertEqual(LearningUnitYear.objects.filter(acronym='LAGRO1200').count(), 1)


class TestFullFormValidateSameEntitiesContainer(LearningUnitFullFormContextMixin):
    """Unit tests for FullForm._validate_same_entities_container()"""

    def test_when_same_entities_container(self):
        form = _instanciate_form(self.current_academic_year, post_data=self.post_data, person=self.person,
                                 start_year=self.current_academic_year.year)
        self.assertTrue(form.is_valid(), form.errors)

    def test_when_not_same_entities_container_case_container_type_master_thesis(self):
        post_data = self._get_post_data_with_different_entities_container_year(learning_container_year_types.MASTER_THESIS)
        form = _instanciate_form(self.current_academic_year, post_data=post_data,
                                 start_year=self.current_academic_year.year)
        self.assertFalse(form.is_valid())

    def test_when_not_same_entities_container_case_container_type_internship(self):
        post_data = self._get_post_data_with_different_entities_container_year(learning_container_year_types.INTERNSHIP)
        form = _instanciate_form(self.current_academic_year, post_data=post_data, person=self.person,
                                 start_year=self.current_academic_year.year)
        self.assertFalse(form.is_valid())

    def test_when_not_same_entities_container_case_container_type_dissertation(self):
        post_data = self._get_post_data_with_different_entities_container_year(learning_container_year_types.DISSERTATION)
        form = _instanciate_form(self.current_academic_year, post_data=post_data, person=self.person,
                                 start_year=self.current_academic_year.year)
        self.assertFalse(form.is_valid())

    def _get_post_data_with_different_entities_container_year(self, container_type):
        container_year = LearningContainerYearFactory.build(academic_year=self.current_academic_year,
                                                            container_type=container_type)
        learning_unit_year = LearningUnitYearFactory.build(academic_year=self.current_academic_year,
                                                           learning_container_year=container_year,
                                                           subtype=learning_unit_year_subtypes.FULL)
        post_data = get_valid_form_data(self.current_academic_year, person=self.person,
                                        learning_unit_year=learning_unit_year)
        post_data['entitycontaineryear_set-1-entity'] = EntityVersionFactory().id
        return post_data
