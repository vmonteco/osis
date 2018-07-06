from unittest.mock import patch
from base.forms.education_group.group import GroupModelForm
from base.forms.education_group.mini_training import MiniTrainingForm, MiniTrainingModelForm
from base.models.education_group import EducationGroup
from base.models.education_group_type import EducationGroupType
from base.models.education_group_year import EducationGroupYear
from base.models.enums import education_group_categories
from base.models.group_element_year import GroupElementYear
from base.tests.factories.education_group_type import EducationGroupTypeFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.entity_version import MainEntityVersionFactory
from base.tests.factories.group_element_year import GroupElementYearFactory
from base.tests.forms.education_group.test_common import _get_valid_post_data, EducationGroupYearMixin, \
    TestCommonBaseFormIsValid
from django.test import TestCase


class TestSave(TestCase):
    """Unit tests on MiniTrainingForm.save()"""

    def setUp(self):
        self.category = education_group_categories.MINI_TRAINING
        self.expected_educ_group_year, self.post_data = _get_valid_post_data(self.category)

    @patch('base.models.education_group_type.find_authorized_types', return_value=EducationGroupType.objects.all())
    def test_create_with_parent(self, mock_find_authorized_types):
        parent = EducationGroupYearFactory()

        form = MiniTrainingForm(data=self.post_data, parent=parent)
        self.assertTrue(form.is_valid(), form.errors)
        created_education_group_year = form.save()

        group_element_year = GroupElementYear.objects.filter(parent=parent, child_branch=created_education_group_year)
        self.assertTrue(group_element_year.exists())

    @patch('base.models.education_group_type.find_authorized_types', return_value=EducationGroupType.objects.all())
    def test_update_with_parent_when_existing_group_element_year(self, mock_find_authorized_types):
        parent = EducationGroupYearFactory()

        entity_version = MainEntityVersionFactory()
        initial_educ_group_year = EducationGroupYearFactory(administration_entity=entity_version.entity)

        GroupElementYearFactory(parent=parent, child_branch=initial_educ_group_year)
        initial_count = GroupElementYear.objects.all().count()

        form = MiniTrainingForm(data=self.post_data, instance=initial_educ_group_year, parent=parent)
        self.assertTrue(form.is_valid(), form.errors)
        form.save()

        # Assert existing GroupElementYear is reused.
        self.assertEqual(initial_count, GroupElementYear.objects.all().count())


class TestMiniTrainingModelForm(EducationGroupYearMixin):

    def setUp(self):
        self.education_group_type = EducationGroupTypeFactory(category=education_group_categories.MINI_TRAINING)
        self.form_class = MiniTrainingModelForm
        super(TestMiniTrainingModelForm, self).setUp(education_group_type=self.education_group_type)

    def test_fields(self):
        fields = ("acronym", "partial_acronym", "education_group_type", "title", "title_english", "credits",
                  "main_teaching_campus", "academic_year", "remark", "remark_english", "min_credits", "max_credits",
                  "administration_entity")

        form = GroupModelForm(parent=None)
        self.assertCountEqual(tuple(form.fields.keys()), fields)

    def test_init_academic_year_field(self):
        self._test_init_academic_year_field(self.form_class)

    def test_init_education_group_type_field(self):
        self._test_init_education_group_type_field(self.form_class, education_group_categories.MINI_TRAINING)

    def test_preselect_entity_version_from_entity_value(self):
        self._test_preselect_entity_version_from_entity_value(self.form_class)