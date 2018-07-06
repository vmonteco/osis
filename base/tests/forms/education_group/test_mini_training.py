from base.forms.education_group.group import GroupModelForm
from base.forms.education_group.mini_training import MiniTrainingModelForm
from base.models.enums import education_group_categories
from base.tests.factories.education_group_type import EducationGroupTypeFactory
from base.tests.forms.education_group.test_common import EducationGroupYearMixin


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