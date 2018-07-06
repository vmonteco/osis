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
from base.models.education_group import EducationGroup
from base.models.education_group_type import EducationGroupType
from base.models.education_group_year import EducationGroupYear
from base.models.entity_version import EntityVersion
from base.tests.factories.education_group import EducationGroupFactory
from base.tests.factories.entity import EntityFactory
from base.tests.factories.authorized_relationship import AuthorizedRelationshipFactory
from django.test import TestCase

from base.forms.education_group.create import CreateEducationGroupYearForm, MiniTrainingForm, MiniTrainingModelForm
from base.models.enums import education_group_categories, organization_type, entity_type
from base.models.group_element_year import GroupElementYear
from base.tests.factories.academic_year import AcademicYearFactory, create_current_academic_year
from base.tests.factories.campus import CampusFactory
from base.tests.factories.education_group_type import EducationGroupTypeFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.entity_version import MainEntityVersionFactory, EntityVersionFactory


class EducationGroupYearMixin(TestCase):
    education_group_type = None

    @classmethod
    def setUp(cls, **kwargs):
        cls.education_group_type = kwargs.pop('education_group_type')

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

    # def _test_create(self, form_class):
    #     form = form_class(data=self.form_data, parent=None)
    #
    #     self.assertTrue(form.is_valid(), form.errors)
    #
    #     education_group_year = form.save()
    #
    #     self.assertEqual(education_group_year.education_group.start_year, self.academic_year.year)
    #     self.assertIsNone(education_group_year.education_group.end_year)

    # def _test_create_with_parent(self, form_class):
    #     AuthorizedRelationshipFactory(parent_type=self.parent_education_group_year.education_group_type,
    #                                   child_type=self.education_group_type)
    #     form = form_class(data=self.form_data, parent=self.parent_education_group_year)
    #
    #     self.assertTrue(form.is_valid(), form.errors)
    #
    #     education_group_year = form.save()
    #
    #     self.assertTrue(GroupElementYear.objects.get(child_branch=education_group_year,
    #                                                  parent=self.parent_education_group_year))

    def _test_update(self):
        pass # ne pas créer un 2e educationGroup et réutilsirerr le premier.


class TestCreateEducationGroupYearForm(EducationGroupYearMixin):

    def setUp(self):
        self.education_group_type = EducationGroupTypeFactory(category=education_group_categories.GROUP)
        self.form_class = CreateEducationGroupYearForm
        super(TestCreateEducationGroupYearForm, self).setUp(education_group_type=self.education_group_type)

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

    def test_create(self):
        form = self.form_class(data=self.form_data, parent=None)

        self.assertTrue(form.is_valid(), form.errors)

        education_group_year = form.save()

        self.assertEqual(education_group_year.education_group.start_year, self.academic_year.year)
        self.assertIsNone(education_group_year.education_group.end_year)

    def test_create_with_parent(self):
        AuthorizedRelationshipFactory(parent_type=self.parent_education_group_year.education_group_type,
                                      child_type=self.education_group_type)
        form = self.form_class(data=self.form_data, parent=self.parent_education_group_year)

        self.assertTrue(form.is_valid(), form.errors)

        education_group_year = form.save()

        self.assertTrue(GroupElementYear.objects.get(child_branch=education_group_year,
                                                     parent=self.parent_education_group_year))

    def test_update(self):
        pass # should assert reuse EducationGroup


class TestIsValid(TestCase):
    """Unit tests on TestMiniTrainingForm.is_valid()"""

    def setUp(self):
        self.category = education_group_categories.MINI_TRAINING

    @patch('base.forms.education_group.create.MiniTrainingModelForm.is_valid', return_value=False)
    def test_when_mini_training_form_is_not_valid(self, mock_is_valid):
        expected_educ_group_year, post_data = _get_valid_post_data(self.category)
        self.assertFalse(MiniTrainingForm(post_data).is_valid())

    @patch('base.forms.education_group.create.EducationGroupModelForm.is_valid', return_value=False)
    def test_when_education_group_model_form_is_not_valid(self, mock_is_valid):
        expected_educ_group_year, post_data = _get_valid_post_data(self.category)
        self.assertFalse(MiniTrainingForm(post_data).is_valid())

    @patch('base.forms.education_group.create.MiniTrainingModelForm.is_valid', return_value=True)
    @patch('base.forms.education_group.create.EducationGroupModelForm.is_valid', return_value=True)
    def test_when_both_of_two_forms_are_valid(self, mock_is_valid, mock_mintraining_is_valid):
        expected_educ_group_year, post_data = _get_valid_post_data(self.category)
        self.assertTrue(MiniTrainingForm(post_data).is_valid())

    def test_post_with_errors(self):
        expected_educ_group_year, post_data = _get_valid_post_data(self.category)
        post_data['administration_entity'] = None
        post_data['end_year'] = "some text"
        form = MiniTrainingForm(data=post_data, parent=None)
        self.assertFalse(form.is_valid(), form.errors)
        self.assertEqual(len(form.errors), 2)


class TestSave(TestCase):
    """Unit tests on TestMiniTrainingForm.save()"""

    def setUp(self):
        self.category = education_group_categories.MINI_TRAINING
        self.expected_educ_group_year, self.post_data = _get_valid_post_data(self.category)

    def _assert_all_fields_correctly_saved(self, education_group_year_saved):
        for field_name in self.post_data.keys():
            if hasattr(self.expected_educ_group_year, field_name):
                expected_value = getattr(self.expected_educ_group_year, field_name, None)
                value = getattr(education_group_year_saved, field_name, None)
            else:
                expected_value = getattr(self.expected_educ_group_year.education_group, field_name, None)
                value = getattr(education_group_year_saved.education_group, field_name, None)
            self.assertEqual(expected_value, value)

    def test_create(self):
        form = MiniTrainingForm(data=self.post_data, parent=None)
        self.assertTrue(form.is_valid(), form.errors)
        created_education_group_year = form.save()

        self.assertEqual(EducationGroupYear.objects.all().count(), 1)
        self.assertEqual(EducationGroup.objects.all().count(), 1)

        self._assert_all_fields_correctly_saved(created_education_group_year)

    def test_update(self):
        entity_version = MainEntityVersionFactory()
        initial_educ_group_year = EducationGroupYearFactory(administration_entity=entity_version.entity)
        initial_educ_group = initial_educ_group_year.education_group

        form = MiniTrainingForm(data=self.post_data, instance=initial_educ_group_year, parent=None)
        self.assertTrue(form.is_valid(), form.errors)
        updated_educ_group_year = form.save()

        self.assertEqual(updated_educ_group_year.pk, initial_educ_group_year.pk)
        self.assertEqual(updated_educ_group_year.education_group, initial_educ_group) # Assert keep the same EducationGroup when update
        self._assert_all_fields_correctly_saved(updated_educ_group_year)


class TestMiniTrainingModelForm(EducationGroupYearMixin):

    def setUp(self):
        self.education_group_type = EducationGroupTypeFactory(category=education_group_categories.MINI_TRAINING)
        self.form_class = MiniTrainingModelForm
        super(TestMiniTrainingModelForm, self).setUp(education_group_type=self.education_group_type)

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

    @patch('base.models.education_group_type.find_authorized_types', return_value=EducationGroupType.objects.all())
    def test_create_with_parent(self, mock_find_authorized_types):
        parent = EducationGroupYearFactory()
        expected_educ_group_year, post_data = _get_valid_post_data(education_group_categories.MINI_TRAINING)
        form = MiniTrainingForm(data=post_data, parent=parent)
        self.assertTrue(form.is_valid(), form.errors)
        created_education_group_year = form.save()
        group_element_year = GroupElementYear.objects.filter(parent=parent, child_branch=created_education_group_year)
        self.assertTrue(group_element_year.exists())


def _get_valid_post_data(category):
    entity_version = MainEntityVersionFactory()
    education_group_type = EducationGroupTypeFactory(category=category)
    campus = CampusFactory(organization__type=organization_type.MAIN)
    fake_education_group_year = EducationGroupYearFactory.build(
        academic_year=create_current_academic_year(),
        administration_entity=entity_version.entity,
        main_teaching_campus=campus,
        education_group_type=education_group_type
    )
    AuthorizedRelationshipFactory(child_type=fake_education_group_year.education_group_type)
    post_data = {
        'main_teaching_campus': str(fake_education_group_year.main_teaching_campus.id),
        'administration_entity': str(entity_version.id),
        'remark_english': str(fake_education_group_year.remark_english),
        'title_english': str(fake_education_group_year.title_english),
        'education_group_type': str(fake_education_group_year.education_group_type.id),
        'partial_acronym': str(fake_education_group_year.partial_acronym),
        'end_year': str(fake_education_group_year.education_group.end_year),
        'start_year': str(fake_education_group_year.education_group.start_year),
        'title': str(fake_education_group_year.title),
        'credits': str(fake_education_group_year.credits),
        'academic_year': str(fake_education_group_year.academic_year.id),
        'max_credits': str(fake_education_group_year.max_credits),
        'min_credits': str(fake_education_group_year.min_credits),
        'remark': str(fake_education_group_year.remark),
        'acronym': str(fake_education_group_year.acronym),
    }
    return fake_education_group_year, post_data
