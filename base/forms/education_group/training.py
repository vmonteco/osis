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
from ajax_select import register, LookupChannel
from ajax_select.fields import AutoCompleteSelectMultipleField
from django import forms
from django.utils.translation import ugettext_lazy as _

from base.forms.learning_unit.entity_form import EntitiesVersionChoiceField
from base.models import education_group_type, campus
from base.models.education_group import EducationGroup
from base.models.education_group_year import EducationGroupYear
from base.models.entity_version import find_main_entities_version, get_last_version
from base.models.enums import education_group_categories
from reference.models.domain import Domain
from base.models.group_element_year import GroupElementYear


class TrainingEducationGroupYearForm(forms.ModelForm):

    domains = AutoCompleteSelectMultipleField(
        'domains', required=False, help_text=None, label=_('domains'),
        plugin_options={'max-height': '100px', 'overflow-y': 'auto', 'overflow-x': 'hidden'})

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
                  "max_credits", "administration_entity", "management_entity", "domains"]

        field_classes = {
            "administration_entity": EntitiesVersionChoiceField,
            "management_entity": EntitiesVersionChoiceField,
        }

    def __init__(self, *args, **kwargs):
        self.parent_education_group_year = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)
        self.prepare_fields()

    def prepare_fields(self):
        self.fields["main_teaching_campus"].queryset = campus.find_main_campuses()

        self.fields["education_group_type"].queryset = self._get_authorized_education_group_types_queryset()
        self.fields["education_group_type"].required = True

        if self.parent_education_group_year:
            self.fields["academic_year"].initial = self.parent_education_group_year.academic_year.id
            self.fields["academic_year"].disabled = True
            self.fields["academic_year"].required = False

        self.fields["administration_entity"].queryset = find_main_entities_version()
        if getattr(self.instance, 'administration_entity', None):
            self.initial['administration_entity'] = get_last_version(self.instance.administration_entity).pk

        self.fields["education_group"].required = False

        self.fields["management_entity"].queryset = find_main_entities_version()
        if getattr(self.instance, 'management_entity', None):
            self.initial['management_entity'] = get_last_version(self.instance.management_entity).pk

    def save(self):
        education_group_year = super().save(commit=False)
        education_group_year.education_group = self._create_education_group()
        education_group_year.save()

        if self.parent_education_group_year:
            self._create_group_element_year(self.parent_education_group_year, education_group_year)

        education_group_year.save_m2m()
        return education_group_year

    def _create_education_group(self):
        start_year = self.cleaned_data["academic_year"].year
        return EducationGroup.objects.create(start_year=start_year)

    @staticmethod
    def _create_group_element_year(parent, child):
        return GroupElementYear.objects.create(parent=parent, child_branch=child)

    def _get_authorized_education_group_types_queryset(self):
        parent_group_type = None
        if self.parent_education_group_year:
            parent_group_type = self.parent_education_group_year.education_group_type
        return education_group_type.find_authorized_types(
            category=education_group_categories.TRAINING, parent_type=parent_group_type
        )


class EducationGroupForm(forms.ModelForm):
    class Meta:
        model = EducationGroup
        fields = ['start_year', 'end_year']


@register('domains')
class DomainsLookup(LookupChannel):

    model = Domain

    def get_query(self, q, request):
        return self.model.objects.filter(name__icontains=q)

    def format_item_display(self, item):
        return u"<span class='tag'>%s</span>" % item.name
