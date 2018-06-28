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
from django import forms

from base.forms.learning_unit.entity_form import EntitiesVersionChoiceField
from base.models import campus, education_group_type
from base.models.education_group import EducationGroup
from base.models.education_group_type import EducationGroupType
from base.models.education_group_year import EducationGroupYear
from base.models.entity_version import find_main_entities_version
from base.models.enums import offer_year_entity_type, education_group_categories
from base.models.group_element_year import GroupElementYear
from base.models.offer_year_entity import OfferYearEntity
from django.utils.translation import ugettext_lazy as _
from base.models.enums import education_group_categories
from base.forms.learning_unit.entity_form import EntitiesVersionChoiceField
from base.models.offer_year_domain import OfferYearDomain
from base.forms.utils.emptyfield import EmptyField
from base.forms.education_group.create import CreateOfferYearEntityForm


class EditionEducationGroupYearForm(forms.ModelForm):
    education_group_year = None
    class Meta:
        model = EducationGroupYear
        fields = ["acronym", "partial_acronym", "education_group_type", "title", "title_english",
                  "academic_year", "main_teaching_campus", "remark", "remark_english", "credits", "enrollment_enabled",
                  "partial_deliberation", "academic_type", "admission_exam",
                  "university_certificate", "duration", "duration_unit", "dissertation",
                  "internship", "primary_language", "other_language_activities",
                  "keywords", "active", "schedule_type",
                  "education_group", "enrollment_campus",
                  "other_campus_activities", "funding", "funding_direction", "funding_cud",
                  "funding_direction_cud",
                  "diploma_printing_title", "diploma_printing_orientation", "professional_title", "min_credits",
                  "max_credits"]

    def __init__(self, *args, **kwargs):
        self.education_group_year = kwargs.get('instance', None)
        self.instance = self.education_group_year
        super().__init__(*args, **kwargs)
        self.prepare_fields()
        self.fields["academic_year"].required = False
        self.fields["education_group"].required = False

    def prepare_fields(self):
        self.fields["main_teaching_campus"].queryset = campus.find_main_campuses()
        self.fields["education_group_type"].queryset = \
            education_group_type.find_by_category(education_group_categories.GROUP)

    def save(self, **kwargs):
        instance = super().save(**kwargs)
        print(instance)
        return instance
    # def save(self, **kwargs):
    #     print('save')
    #     print(self.instance)
    #     instance = super().save(**kwargs)
    #     return instance
    #
    # def clean_academic_year(self):
    #     print('clean_academic_year')
    #     data_cleaned = self.cleaned_data.get('academic_year')
    #     print(data_cleaned)
    #     if data_cleaned:
    #         return data_cleaned

    def clean(self):
        print(self.instance)
        print('clean')
        cleaned_data = self.cleaned_data

        print(self.education_group_year.academic_year)
        cleaned_data['academic_year'] = self.education_group_year.academic_year
        cleaned_data['education_group'] = self.education_group_year.education_group
        print(cleaned_data)
        return cleaned_data


class EducationGroupForm(forms.ModelForm):

    class Meta:
        model = EducationGroup
        fields = ['start_year', 'end_year']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class EducationGroupForm(forms.ModelForm):

    class Meta:
        model = EducationGroup
        fields = ['start_year', 'end_year']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class EducationGroupTypeForm(forms.ModelForm):
    class Meta:
        model = EducationGroupType
        fields = ['category', 'name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class UpdateOfferYearManagementEntityForm(CreateOfferYearEntityForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["entity"].label = _('management_entity')