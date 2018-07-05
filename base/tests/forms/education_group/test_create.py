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
from unittest.mock import patch
from base.models.entity_version import EntityVersion
from base.tests.factories.entity import EntityFactory
from base.tests.factories.authorized_relationship import AuthorizedRelationshipFactory
from django.test import TestCase

from base.forms.education_group.create import CreateEducationGroupYearForm, MiniTrainingForm, MiniTrainingModelForm
from base.models.enums import education_group_categories, organization_type
from base.models.group_element_year import GroupElementYear
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.campus import CampusFactory
from base.tests.factories.education_group_type import EducationGroupTypeFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.entity_version import MainEntityVersionFactory, EntityVersionFactory


class EducationGroupYearMixin(TestCase):
    @classmethod
    def setUp(cls):
        cls.education_group_type = EducationGroupTypeFactory(category=education_group_categories.GROUP)
        cls.campus = CampusFactory(organization__type=organization_type.MAIN)
        cls.academic_year = AcademicYearFactory()
        new_entity_version = MainEntityVersionFactory()

        cls.form_data = {
            "acronym": "ACRO4569",
            "partial_acronym": "PACR8974",
            "education_group_type": cls.education_group_type.id,
            "title": "Test data",
            "main_teaching_campus": cls.campus.id,
            "academic_year": cls.academic_year.id,
            "administration_entity": new_entity_version.pk,
            "remark": "This is a test!!"
        }

        cls.parent_education_group_year = EducationGroupYearFactory(academic_year=cls.academic_year)
        cls.entity_version = EntityVersionFactory(entity=cls.parent_education_group_year.administration_entity)

    def _test_init_academic_year_field(self, form_class):
        form = form_class(parent=self.parent_education_group_year)

        academic_year_field = form.fields["academic_year"]
        self.assertTrue(academic_year_field.disabled)
        self.assertTrue(academic_year_field.disabled)
        self.assertTrue(academic_year_field.initial, self.academic_year)

    @patch('base.models.education_group_type.find_authorized_types')
    def _test_init_education_group_type_field(self, form_class, expected_category, mock_authorized_types):
        form_class(parent=self.parent_education_group_year)
        self.assertTrue(mock_authorized_types.called)
        expected_kwargs = {
            'category': expected_category,
            'parent_type': self.parent_education_group_year.education_group_type
        }
        mock_authorized_types.assert_called_with(**expected_kwargs)

    def _test_preselect_entity_version_from_entity_value(self, form_class):
        form = form_class(instance=self.parent_education_group_year)
        educ_group_entity = self.parent_education_group_year.administration_entity
        expected_entity_version = EntityVersion.objects.filter(entity=educ_group_entity).latest('start_date')
        self.assertEqual(form.initial['administration_entity'], expected_entity_version.id)

    def _test_save(self, form_class):
        form = form_class(data=self.form_data, parent=None)

        self.assertTrue(form.is_valid(), form.errors)

        education_group_year = form.save()

        self.assertEqual(education_group_year.education_group.start_year, self.academic_year.year)
        self.assertIsNone(education_group_year.education_group.end_year)

    def _test_save_with_parent(self, form_class):
        AuthorizedRelationshipFactory(parent_type=self.parent_education_group_year.education_group_type,
                                      child_type=self.education_group_type)
        form = form_class(data=self.form_data, parent=self.parent_education_group_year)

        self.assertTrue(form.is_valid(), form.errors)

        education_group_year = form.save()

        self.assertTrue(GroupElementYear.objects.get(child_branch=education_group_year,
                                                     parent=self.parent_education_group_year))


class TestCreateEducationGroupYearForm(EducationGroupYearMixin):

    def setUp(self):
        super(TestCreateEducationGroupYearForm, self).setUp()
        self.form_class = CreateEducationGroupYearForm

    def test_fields(self):
        fields = ("acronym", "partial_acronym", "education_group_type", "title", "title_english", "credits",
                  "main_teaching_campus", "academic_year", "remark", "remark_english", "min_credits", "max_credits",
                  "administration_entity")

        form = CreateEducationGroupYearForm(parent=None)
        self.assertCountEqual(tuple(form.fields.keys()), fields)

    def test_init_academic_year_field(self):
        self._test_init_academic_year_field(self.form_class)

    def test_init_education_group_type_field(self):
        self._test_init_education_group_type_field(self.form_class, education_group_categories.GROUP)

    def test_preselect_entity_version_from_entity_value(self):
        self._test_preselect_entity_version_from_entity_value(self.form_class)

    def test_save(self):
        self._test_save(self.form_class)

    def test_save_with_parent(self):
        self._test_save_with_parent(self.form_class)


class TestMiniTrainingForm(TestCase):

    class TestInit(TestCase):
        pass # Nothing to test

    class TestIsValid(TestCase):

        @patch('base.forms.education_group.create.MiniTrainingModelForm.is_valid', return_value=False)
        def test_when_mini_training_form_is_not_valid(self):
            self.assertFalse(MiniTrainingForm(_get_post_data()).is_valid())

        @patch('base.forms.education_group.create.EducationGroupModelForm.is_valid', return_value=False)
        def test_when_education_group_model_form_is_not_valid(self):
            self.assertFalse(MiniTrainingForm(_get_post_data()).is_valid())

        @patch('base.forms.education_group.create.MiniTrainingModelForm.is_valid', return_value=True)
        @patch('base.forms.education_group.create.EducationGroupModelForm.is_valid', return_value=True)
        def test_when_both_of_two_forms_are_valid(self):
            self.assertTrue(MiniTrainingForm(_get_post_data()).is_valid())

    class TestSave(TestCase):
        def test_assert_education_group_is_linked_to_education_group_year(self):
            # test on creation
            pass

        def test_all_fields_saved_in_education_group_year(self):
            pass

        def test_all_fields_saved_in_education_group(self):
            pass


class TestMiniTrainingModelForm(EducationGroupYearMixin):

    def setUp(self):
        super(TestMiniTrainingModelForm, self).setUp()
        self.form_class = MiniTrainingModelForm

    def test_fields(self):
        fields = ("acronym", "partial_acronym", "education_group_type", "title", "title_english", "credits",
                  "main_teaching_campus", "academic_year", "remark", "remark_english", "min_credits", "max_credits",
                  "administration_entity")

        form = CreateEducationGroupYearForm(parent=None)
        self.assertCountEqual(tuple(form.fields.keys()), fields)

    def test_init_academic_year_field(self):
        self._test_init_academic_year_field(self.form_class)

    def test_init_education_group_type_field(self):
        self._test_init_education_group_type_field(self.form_class, education_group_categories.MINI_TRAINING)

    def test_preselect_entity_version_from_entity_value(self):
        self._test_preselect_entity_version_from_entity_value(self.form_class)

    def test_save(self):
        self._test_save(self.form_class)

    def test_save_with_parent(self):
        self._test_save_with_parent(self.form_class)


def _get_post_data(academic_year=None):
    if not academic_year:
        academic_year = AcademicYearFactory()
    return {
        'main_teaching_campus': str(CampusFactory().id),
        'administration_entity': str(EntityFactory().id),
        'remark_english': 'Test remark English',
        'title_english': "Law's minor",
        'education_group_type': str(EducationGroupTypeFactory().id),
        'partial_acronym': 'LODRT100I',
        'end_year': '',
        'start_year': '2015',
        'title': 'Mineure en droit (ouverture)',
        'credits': '30.00',
        'academic_year': str(academic_year.id),
        'max_credits': '5',
        'min_credits': '15',
        'remark': 'test remark',
        'acronym': 'MINODROI'
    }
