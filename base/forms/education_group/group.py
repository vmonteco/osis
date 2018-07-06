from base.forms.education_group.common import MainEntitiesVersionChoiceField, MainTeachingCampusChoiceField, \
    init_education_group_type_field, init_academic_year, preselect_entity_version_from_entity_value, \
    CommonBaseForm, EducationGroupModelForm
from base.models.education_group_year import EducationGroupYear
from base.models.enums import education_group_categories
from django import forms


class GroupModelForm(forms.ModelForm):

    class Meta:
        model = EducationGroupYear
        fields = ("acronym", "partial_acronym", "education_group_type", "title", "title_english", "credits",
                  "main_teaching_campus", "academic_year", "remark", "remark_english", "min_credits", "max_credits",
                  "administration_entity")
        field_classes = {
            "administration_entity": MainEntitiesVersionChoiceField,
            "main_teaching_campus": MainTeachingCampusChoiceField
        }

    def __init__(self, *args, **kwargs):
        self.parent = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)
        init_education_group_type_field(self.fields["education_group_type"],
                                         self.parent,
                                         education_group_categories.GROUP)
        init_academic_year(self.fields["academic_year"], self.parent)

        preselect_entity_version_from_entity_value(self)


class GroupForm(CommonBaseForm):

    def __init__(self, data, instance=None, parent=None):
        educ_group_year_form = GroupModelForm(data, instance=instance, parent=parent)

        education_group = instance.education_group if instance else None

        educ_group_model_form = EducationGroupModelForm({}, instance=education_group)

        super(GroupForm, self).__init__(educ_group_year_form, educ_group_model_form)