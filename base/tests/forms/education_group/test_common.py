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
from unittest.mock import patch

from django.forms import ModelForm
from django.test import TestCase

from base.forms.education_group.common import EducationGroupModelForm, CommonBaseForm
from base.forms.education_group.mini_training import MiniTrainingYearModelForm, MiniTrainingForm
from base.models.academic_year import current_academic_year
from base.models.education_group import EducationGroup
from base.models.education_group_type import EducationGroupType
from base.models.education_group_year import EducationGroupYear
from base.models.entity_version import EntityVersion
from base.models.enums import organization_type, education_group_categories
from base.models.enums.constraint_type import CREDITS
from base.models.enums.education_group_categories import TRAINING
from base.models.group_element_year import GroupElementYear
from base.tests.factories.academic_year import AcademicYearFactory, create_current_academic_year
from base.tests.factories.authorized_relationship import AuthorizedRelationshipFactory
from base.tests.factories.campus import CampusFactory
from base.tests.factories.education_group_type import EducationGroupTypeFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.entity_version import MainEntityVersionFactory, EntityVersionFactory
from base.tests.factories.group_element_year import GroupElementYearFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.person_entity import PersonEntityFactory


class EducationGroupYearModelFormMixin(TestCase):
    """Common class used to get common tests on ModelForm instances of Training, MiniTraining and Group"""
    education_group_type = None

    def setUp(self, **kwargs):
        self.education_group_type = kwargs.pop('education_group_type')

        self.campus = CampusFactory(organization__type=organization_type.MAIN)
        self.academic_year = AcademicYearFactory()
        new_entity_version = MainEntityVersionFactory()

        self.form_data = {
            "acronym": "ACRO4569",
            "partial_acronym": "PACR8974",
            "education_group_type": self.education_group_type.id,
            "title": "Test data",
            "main_teaching_campus": self.campus.id,
            "academic_year": self.academic_year.id,
            "management_entity": new_entity_version.pk,
            "remark": "This is a test!!"
        }

        self.parent_education_group_year = EducationGroupYearFactory(academic_year=self.academic_year)
        # Append version to management/administration entity
        self.entity_version = EntityVersionFactory(entity=self.parent_education_group_year.management_entity)
        if self.education_group_type.category == TRAINING:
            EntityVersionFactory(entity=self.parent_education_group_year.administration_entity)

        # Create user and attached it to management entity
        person = PersonFactory()
        PersonEntityFactory(
            person=person,
            entity=self.parent_education_group_year.management_entity
        )
        self.user = person.user

    def _test_fields(self, form_class, fields):
        form = form_class(parent=None, user=self.user, education_group_type=self.education_group_type)
        self.assertCountEqual(tuple(form.fields.keys()), fields)

    @patch('base.forms.education_group.common.find_authorized_types')
    def _test_init_and_disable_academic_year_field(self, form_class, mock_authorized_types):
        mock_authorized_types.return_value = EducationGroupType.objects.all()
        form = form_class(
            parent=self.parent_education_group_year,
            education_group_type=self.education_group_type,
            user=self.user,
        )

        academic_year_field = form.fields["academic_year"]
        self.assertTrue(academic_year_field.disabled)
        self.assertTrue(academic_year_field.initial, self.academic_year)

    @patch('base.forms.education_group.common.find_authorized_types')
    def _test_init_education_group_type_field(self, form_class, expected_category, mock_authorized_types):
        mock_authorized_types.return_value = EducationGroupType.objects.all()

        form_class(
            parent=self.parent_education_group_year,
            education_group_type=self.education_group_type,
            user=self.user
        )

        self.assertTrue(mock_authorized_types.called)
        expected_args = [
            expected_category,
            self.parent_education_group_year
        ]
        mock_authorized_types.assert_called_with(*expected_args)

    def _test_preselect_entity_version_from_entity_value(self, form_class):
        form = form_class(instance=self.parent_education_group_year, user=self.user)
        educ_group_entity = self.parent_education_group_year.management_entity
        expected_entity_version = EntityVersion.objects.filter(entity=educ_group_entity).latest('start_date')
        self.assertEqual(form.initial['management_entity'], expected_entity_version.id)

    @patch('base.forms.education_group.common.find_authorized_types')
    def _test_preselect_management_entity_from_parent(self, form_class, mock_authorized_types):
        mock_authorized_types.return_value = EducationGroupType.objects.all()

        form = form_class(
            parent=self.parent_education_group_year,
            education_group_type=self.education_group_type,
            user=self.user
        )
        self.assertEqual(
            form.fields["management_entity"].initial,
            self.parent_education_group_year.management_entity_version,
        )


class TestCommonBaseFormIsValid(TestCase):
    """Unit tests on CommonBaseForm.is_valid()"""

    def setUp(self):
        self.category = education_group_categories.MINI_TRAINING  # Could take GROUP or TRAINING, the result is the same
        fake_educ_group_year, self.post_data = _get_valid_post_data(self.category)
        self.egt = fake_educ_group_year.education_group_type

        # Create user and attached it to management entity
        person = PersonFactory()
        PersonEntityFactory(person=person, entity=fake_educ_group_year.management_entity)
        self.user = person.user

        self.education_group_year_form = MiniTrainingYearModelForm(
            self.post_data,
            user=self.user,
            education_group_type=self.egt,
        )
        self.education_group_form = EducationGroupModelForm(
            self.post_data,
            user=self.user
        )

    @patch('base.forms.education_group.mini_training.MiniTrainingModelForm.is_valid', return_value=False)
    def _test_when_mini_training_form_is_not_valid(self, mock_is_valid):
        self.assertFalse(
            CommonBaseForm(
                self.post_data,
                user=self.user,
                education_group_type=self.egt
            ).is_valid()
        )

    @patch('base.forms.education_group.common.EducationGroupModelForm.is_valid', return_value=False)
    def test_when_education_group_model_form_is_not_valid(self, mock_is_valid):
        self.assertFalse(
            MiniTrainingForm(
                self.post_data,
                user=self.user,
                education_group_type=self.egt
            ).is_valid()
        )

    @patch('base.forms.education_group.mini_training.MiniTrainingModelForm.is_valid', return_value=True)
    @patch('base.forms.education_group.common.CommonBaseForm._post_clean', return_value=True)
    @patch('base.forms.education_group.common.EducationGroupModelForm.is_valid', return_value=True)
    def test_when_both_of_two_forms_are_valid(self, mock_is_valid, mock_post_clean, mock_mintraining_is_valid):
        self.assertTrue(
            MiniTrainingForm(
                self.post_data,
                user=self.user,
                education_group_type=self.egt
            ).is_valid()
        )

    def test_post_with_errors(self):
        expected_educ_group_year, wrong_post_data = _get_valid_post_data(self.category)
        wrong_post_data['management_entity'] = None
        wrong_post_data['end_year'] = "some text"
        wrong_post_data["max_constraint"] = expected_educ_group_year.min_constraint - 1

        form = MiniTrainingForm(wrong_post_data, education_group_type=self.egt, user=self.user)
        self.assertFalse(form.is_valid(), form.errors)
        self.assertEqual(len(form.errors), 3, form.errors)


class TestCommonBaseFormSave(TestCase):
    """Unit tests on CommonBaseForm.save()"""

    def setUp(self):
        category = education_group_categories.MINI_TRAINING  # Could take GROUP or TRAINING, the result is the same
        self.form_class = MiniTrainingForm  # Could also take GROUP or TRAINING, the result is the same
        self.expected_educ_group_year, self.post_data = _get_valid_post_data(category)
        self.education_group_type = self.expected_educ_group_year.education_group_type

        # Create user and attached it to management entity
        person = PersonFactory()
        PersonEntityFactory(person=person, entity=self.expected_educ_group_year.management_entity)
        self.user = person.user

    def _assert_all_fields_correctly_saved(self, education_group_year_saved):
        for field_name in self.post_data.keys():
            if hasattr(self.expected_educ_group_year, field_name):
                expected_value = getattr(self.expected_educ_group_year, field_name, None)
                value = getattr(education_group_year_saved, field_name, None)
            else:
                expected_value = getattr(self.expected_educ_group_year.education_group, field_name, None)
                value = getattr(education_group_year_saved.education_group, field_name, None)
            self.assertEqual(expected_value, value, field_name)

    def test_update_without_parent(self):
        entity_version = MainEntityVersionFactory()
        initial_educ_group_year = EducationGroupYearFactory(academic_year=current_academic_year(),
                                                            management_entity=entity_version.entity,
                                                            education_group__start_year=current_academic_year().year)

        initial_educ_group = initial_educ_group_year.education_group

        form = self.form_class(
            data=self.post_data,
            instance=initial_educ_group_year,
            parent=None,
            user=self.user
        )
        self.assertTrue(form.is_valid(), form.errors)
        updated_educ_group_year = form.save()

        self.assertEqual(updated_educ_group_year.pk, initial_educ_group_year.pk)
        # Assert keep the same EducationGroup when update
        self.assertEqual(updated_educ_group_year.education_group, initial_educ_group)
        self._assert_all_fields_correctly_saved(updated_educ_group_year)
        self.assertTrue(form.forms[ModelForm].fields["academic_year"].disabled)

    def test_create_without_parent(self):
        initial_count = GroupElementYear.objects.all().count()

        form = self.form_class(
            data=self.post_data,
            parent=None,
            education_group_type=self.education_group_type,
            user=self.user
        )
        self.assertTrue(form.is_valid(), form.errors)
        created_education_group_year = form.save()

        self.assertEqual(EducationGroupYear.objects.all().count(), 1)
        self.assertEqual(EducationGroup.objects.all().count(), 1)

        self._assert_all_fields_correctly_saved(created_education_group_year)
        self.assertEqual(initial_count, GroupElementYear.objects.all().count())
        self.assertFalse(form.forms[ModelForm].fields["academic_year"].disabled)

    @patch('base.forms.education_group.common.find_authorized_types', return_value=EducationGroupType.objects.all())
    def test_create_with_parent(self, mock_find_authorized_types):
        parent = EducationGroupYearFactory(academic_year=self.expected_educ_group_year.academic_year)
        AuthorizedRelationshipFactory(child_type=self.education_group_type)

        form = self.form_class(
            data=self.post_data,
            parent=parent,
            education_group_type=self.education_group_type,
            user=self.user
        )

        self.assertTrue(form.is_valid(), form.errors)
        created_education_group_year = form.save()

        group_element_year = GroupElementYear.objects.filter(parent=parent, child_branch=created_education_group_year)
        self.assertTrue(group_element_year.exists())
        self._assert_all_fields_correctly_saved(created_education_group_year)
        self.assertTrue(form.forms[ModelForm].fields["academic_year"].disabled)

    @patch('base.forms.education_group.common.find_authorized_types', return_value=EducationGroupType.objects.all())
    def test_update_with_parent_when_existing_group_element_year(self, mock_find_authorized_types):
        parent = EducationGroupYearFactory(academic_year=self.expected_educ_group_year.academic_year)

        entity_version = MainEntityVersionFactory()
        initial_educ_group_year = EducationGroupYearFactory(management_entity=entity_version.entity,
                                                            academic_year=self.expected_educ_group_year.academic_year,
                                                            education_group__start_year=current_academic_year().year)

        GroupElementYearFactory(parent=parent, child_branch=initial_educ_group_year)
        initial_count = GroupElementYear.objects.all().count()

        form = self.form_class(
            data=self.post_data,
            instance=initial_educ_group_year,
            parent=parent,
            user=self.user
        )
        self.assertTrue(form.is_valid(), form.errors)
        updated_education_group_year = form.save()

        # Assert existing GroupElementYear is reused.
        self.assertEqual(initial_count, GroupElementYear.objects.all().count())
        self._assert_all_fields_correctly_saved(updated_education_group_year)
        self.assertTrue(form.forms[ModelForm].fields["academic_year"].disabled)

    def test_create_when_no_start_year_is_posted(self):
        data = dict(self.post_data)
        data['start_year'] = None
        form = self.form_class(
            data=self.post_data,
            parent=None,
            education_group_type=self.education_group_type,
            user=self.user
        )
        self.assertTrue(form.is_valid(), form.errors)
        created_education_group_year = form.save()

        self.assertEqual(created_education_group_year.education_group.start_year,
                         created_education_group_year.academic_year.year)


def _get_valid_post_data(category):
    entity_version = MainEntityVersionFactory()
    education_group_type = EducationGroupTypeFactory(category=category)
    campus = CampusFactory(organization__type=organization_type.MAIN)
    current_academic_year = create_current_academic_year()
    fake_education_group_year = EducationGroupYearFactory.build(
        academic_year=current_academic_year,
        management_entity=entity_version.entity,
        main_teaching_campus=campus,
        education_group_type=education_group_type,
        education_group__start_year=current_academic_year.year,
        constraint_type=CREDITS,
    )
    AuthorizedRelationshipFactory(child_type=fake_education_group_year.education_group_type)
    post_data = {
        'main_teaching_campus': str(fake_education_group_year.main_teaching_campus.id),
        'management_entity': str(entity_version.id),
        'remark_english': str(fake_education_group_year.remark_english),
        'title_english': str(fake_education_group_year.title_english),
        'partial_acronym': str(fake_education_group_year.partial_acronym),
        'end_year': str(fake_education_group_year.education_group.end_year),
        'start_year': str(fake_education_group_year.education_group.start_year),
        'title': str(fake_education_group_year.title),
        'credits': str(fake_education_group_year.credits),
        'academic_year': str(fake_education_group_year.academic_year.id),
        'constraint_type': CREDITS,
        'max_constraint': str(fake_education_group_year.max_constraint),
        'min_constraint': str(fake_education_group_year.min_constraint),
        'remark': str(fake_education_group_year.remark),
        'acronym': str(fake_education_group_year.acronym),
        'active': str(fake_education_group_year.active),
        'schedule_type': str(fake_education_group_year.schedule_type),
    }
    return fake_education_group_year, post_data
