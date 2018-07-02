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

from base.models import campus, education_group_type
from base.models.education_group import EducationGroup
from base.models.education_group_year import EducationGroupYear
from base.models.enums import education_group_categories


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
        super().__init__(*args, **kwargs)
        self.prepare_fields()

    def prepare_fields(self):
        self.fields["academic_year"].required = False
        self.fields["education_group"].required = False
        self.fields["main_teaching_campus"].queryset = campus.find_main_campuses()
        self.fields["education_group_type"].queryset = \
            education_group_type.find_by_category(education_group_categories.TRAINING)
        self.fields["education_group_type"].required = True

    def clean(self):
        cleaned_data = self.cleaned_data
        cleaned_data['academic_year'] = self.education_group_year.academic_year
        cleaned_data['education_group'] = self.education_group_year.education_group
        return cleaned_data


class EducationGroupForm(forms.ModelForm):

    class Meta:
        model = EducationGroup
        fields = ['start_year', 'end_year']
