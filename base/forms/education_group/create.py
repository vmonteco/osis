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
import itertools
from django import forms

from base.forms.learning_unit.entity_form import EntitiesVersionChoiceField
from base.models import campus, education_group_type
from base.models.education_group import EducationGroup
from base.models.education_group_year import EducationGroupYear
from base.models.entity_version import find_main_entities_version, get_last_version
from base.models.enums import education_group_categories
from base.models.group_element_year import GroupElementYear


class MainTeachingCampusChoiceField(forms.ModelChoiceField):

    def __init__(self, queryset, *args, **kwargs):
        queryset = campus.find_main_campuses()
        super(MainTeachingCampusChoiceField, self).__init__(queryset, *args, **kwargs)


class MainEntitiesVersionChoiceField(EntitiesVersionChoiceField):
    def __init__(self, queryset, *args, **kwargs):
        queryset = find_main_entities_version()
        super(MainEntitiesVersionChoiceField, self).__init__(queryset, *args, **kwargs)


def _init_education_group_type_field(form_field, parent_education_group_year, category):
    parent_group_type = None
    if parent_education_group_year:
        parent_group_type = parent_education_group_year.education_group_type

    form_field.queryset = education_group_type.find_authorized_types(category=category, parent_type=parent_group_type)
    form_field.required = True


def _init_academic_year(form_field, parent_education_group_year):
    if parent_education_group_year:
        form_field.initial = parent_education_group_year.academic_year.id
        form_field.disabled = True
        form_field.required = False


def _preselect_entity_version_from_entity_value(modelform):
    if getattr(modelform.instance, 'administration_entity', None):
        modelform.initial['administration_entity'] = get_last_version(modelform.instance.administration_entity).pk


class CreateEducationGroupYearForm(forms.ModelForm):

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
        self.parent_education_group_year = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)

        # self.fields["main_teaching_campus"].queryset = campus.find_main_campuses()

        # self.fields["education_group_type"].queryset = self._get_authorized_education_group_types_queryset()
        # self.fields["education_group_type"].required = True
        _init_education_group_type_field(self.fields["education_group_type"],
                                         self.parent_education_group_year,
                                         education_group_categories.GROUP)

        # if self.parent_education_group_year:
        #     self.fields["academic_year"].initial = self.parent_education_group_year.academic_year.id
        #     self.fields["academic_year"].disabled = True
        #     self.fields["academic_year"].required = False
        _init_academic_year(self.fields["academic_year"], self.parent_education_group_year)

        # self.fields["administration_entity"].queryset = find_main_entities_version()

        # if getattr(self.instance, 'administration_entity', None):
        #     self.initial['administration_entity'] = get_last_version(self.instance.administration_entity).pk
        _preselect_entity_version_from_entity_value(self)

    # def _get_authorized_education_group_types_queryset(self):
    #     parent_group_type = None
    #     if self.parent_education_group_year:
    #         parent_group_type = self.parent_education_group_year.education_group_type
    #     return education_group_type.find_authorized_types(
    #         category=education_group_categories.GROUP, parent_type=parent_group_type
    #     )

    def save(self, *args, **kwargs):
        education_group_year = super().save(commit=False)
        education_group_year.education_group = self._create_education_group()
        education_group_year.save()

        if self.parent_education_group_year:
            self._create_group_element_year(self.parent_education_group_year, education_group_year)

        return education_group_year

    def _create_education_group(self):
        start_year = self.cleaned_data["academic_year"].year
        return EducationGroup.objects.create(start_year=start_year)

    @staticmethod
    def _create_group_element_year(parent, child):
        return GroupElementYear.objects.create(parent=parent, child_branch=child)


class EducationGroupModelForm(forms.ModelForm):

    class Meta:
        model = EducationGroup
        fields = ("start_year", "end_year")


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
        self.parent_education_group_year = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)
        _init_education_group_type_field(self.fields["education_group_type"],
                                         self.parent_education_group_year,
                                         education_group_categories.MINI_TRAINING)
        _init_academic_year(self.fields["academic_year"], self.parent_education_group_year)
        _preselect_entity_version_from_entity_value(self) # Due to MainEntitiesVersionChoiceField


class MiniTrainingForm:
    forms = None

    def __init__(self, data, instance=None, parent=None):
        education_group = instance.education_group if instance else None
        self.forms = {
            MiniTrainingModelForm: MiniTrainingModelForm(data, instance=instance, parent=parent),
            EducationGroupModelForm: EducationGroupModelForm(data, instance=education_group)
        }

    def is_valid(self):
        return all([form.is_valid() for form in self.forms.values()])

    def save(self):
        education_group = self.forms[EducationGroupModelForm].save()
        self.forms[MiniTrainingModelForm].instance.education_group = education_group
        return self.forms[MiniTrainingModelForm].save()

    @property
    def errors(self):
        errors = {}
        for form in self.forms.values():
            errors.update(form.errors)
        return errors
