from base.forms.education_group.common import MainEntitiesVersionChoiceField, MainTeachingCampusChoiceField, \
    _init_education_group_type_field, _init_academic_year, _preselect_entity_version_from_entity_value, \
    _save_group_element_year, CommonBaseForm, EducationGroupModelForm
from base.models.education_group_year import EducationGroupYear
from base.models.enums import education_group_categories
from django import forms


class MiniTrainingModelForm(forms.ModelForm):
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
        _init_education_group_type_field(self.fields["education_group_type"],
                                         self.parent,
                                         education_group_categories.MINI_TRAINING)
        _init_academic_year(self.fields["academic_year"], self.parent)
        _preselect_entity_version_from_entity_value(self) # Due to MainEntitiesVersionChoiceField

    def save(self, *args, **kwargs):
        education_group_year = super(MiniTrainingModelForm, self).save(*args, **kwargs)
        _save_group_element_year(self.parent, education_group_year)
        return education_group_year


class MiniTrainingForm(CommonBaseForm):

    def __init__(self, data, instance=None, parent=None):
        education_group_year_form = MiniTrainingModelForm(data, instance=instance, parent=parent)
        education_group = instance.education_group if instance else None
        education_group_form = EducationGroupModelForm(data, instance=education_group)
        super(MiniTrainingForm, self).__init__(education_group_year_form, education_group_form)