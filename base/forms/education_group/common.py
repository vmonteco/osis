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
from django.core.exceptions import PermissionDenied, ImproperlyConfigured
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _

from base.forms.common import ValidationRuleMixin, WarningFormMixin
from base.forms.learning_unit.entity_form import EntitiesVersionChoiceField
from base.models import campus, group_element_year
from base.models.campus import Campus
from base.models.education_group import EducationGroup
from base.models.education_group_type import find_authorized_types, EducationGroupType
from base.models.education_group_year import EducationGroupYear
from base.models.entity_version import find_main_entities_version, get_last_version
from reference.models.language import Language


class MainTeachingCampusChoiceField(forms.ModelChoiceField):
    def __init__(self, queryset, *args, **kwargs):
        queryset = campus.find_main_campuses()
        super(MainTeachingCampusChoiceField, self).__init__(queryset, *args, **kwargs)


class MainEntitiesVersionChoiceField(EntitiesVersionChoiceField):
    def __init__(self, queryset, *args, **kwargs):
        queryset = find_main_entities_version()
        super(MainEntitiesVersionChoiceField, self).__init__(queryset, *args, **kwargs)


class ValidationRuleEducationGroupTypeMixin(WarningFormMixin, ValidationRuleMixin):
    """
    ValidationRuleMixin For EducationGroupType

    The object reference must be structured like that:
        {db_table_name}.{col_name}.{education_group_type_name}
    """
    def field_reference(self, name):
        return super().field_reference(name) + '.' + self.get_type()

    def get_type(self):
        # For creation
        if self.education_group_type:
            return self.education_group_type.name
        # For updating
        elif self.instance and self.instance.education_group_type:
            return self.instance.education_group_type.name

        return ""


class EducationGroupYearModelForm(ValidationRuleEducationGroupTypeMixin, forms.ModelForm):
    category = None

    class Meta:
        model = EducationGroupYear
        field_classes = {
            "management_entity": MainEntitiesVersionChoiceField,
            "main_teaching_campus": MainTeachingCampusChoiceField
        }
        fields = []

    def __init__(self, *args, education_group_type=None, **kwargs):
        self.parent = kwargs.pop("parent", None)

        if not education_group_type and not kwargs.get('instance'):
            raise ImproperlyConfigured("Provide an education_group_type or an instance")

        self.education_group_type = education_group_type
        if self.education_group_type:
            if education_group_type not in find_authorized_types(self.category, self.parent):
                raise PermissionDenied("Unauthorized type {} for {}".format(education_group_type, self.category))

        if "initial" not in kwargs:
            kwargs["initial"] = {}

        # TODO use natural-key to select default value
        # Default campus selected 'Louvain-la-Neuve' if exist
        kwargs['initial']['main_teaching_campus'] = Campus.objects.filter(name='Louvain-la-Neuve').first()
        kwargs['initial']['enrollment_campus'] = Campus.objects.filter(name='Louvain-la-Neuve').first()
        kwargs['initial']['primary_language'] = Language.objects.filter(code='FR').first()

        super().__init__(*args, **kwargs)

        self._filter_education_group_type()
        self._init_and_disable_academic_year()
        self._preselect_entity_version_from_entity_value()

        self.fields["title_english"].warning = True
        self.fields["acronym"].validators.append(RegexValidator("^(W)(.*)$"))

    def _filter_education_group_type(self):
        # When the type is already given, we need to disabled the field
        if self.education_group_type:
            self.instance.education_group_type = self.education_group_type
            self._disable_field("education_group_type", self.education_group_type.pk)

        elif self.instance.pk:
            self._disable_field("education_group_type", self.instance.education_group_type.pk)

    def _init_and_disable_academic_year(self):
        if self.parent or self.instance.academic_year_id:
            academic_year = self.parent.academic_year if self.parent else self.instance.academic_year
            self._disable_field("academic_year", initial_value=academic_year.pk)

    def _preselect_entity_version_from_entity_value(self):
        if getattr(self.instance, 'management_entity', None):
            self.initial['management_entity'] = get_last_version(self.instance.management_entity).pk

    def _disable_field(self, key, initial_value=None):
        field = self.fields[key]
        if initial_value:
            self.fields[key].initial = initial_value

        field.disabled = True
        field.required = False


class EducationGroupModelForm(forms.ModelForm):
    class Meta:
        model = EducationGroup
        fields = ("start_year", "end_year")

    def save(self, *args, start_year=None, **kwargs):
        if start_year:
            self.instance.start_year = start_year
        return super().save(*args, **kwargs)


class CommonBaseForm:
    forms = None

    def __init__(self, education_group_year_form, education_group_form):
        self.forms = {
            forms.ModelForm: education_group_year_form,
            EducationGroupModelForm: education_group_form
        }

    def is_valid(self):
        return all([form.is_valid() for form in self.forms.values()])

    def save(self):
        educ_group_year_form = self.forms[forms.ModelForm]
        educ_group_form = self.forms[EducationGroupModelForm]

        start_year = None
        if self._is_creation() and not educ_group_form.instance.start_year:
            start_year = educ_group_year_form.cleaned_data['academic_year'].year

        education_group = educ_group_form.save(start_year=start_year)
        educ_group_year_form.instance.education_group = education_group
        education_group_year = educ_group_year_form.save()
        self._save_group_element_year(educ_group_year_form.parent, education_group_year)
        return education_group_year

    def _is_creation(self):
        return not self.forms[EducationGroupModelForm].instance.id

    @staticmethod
    def _save_group_element_year(parent, child):
        # TODO :: what if this relation parent/child already exists? Should we create a new GroupElementYear anymore?
        if parent:
            group_element_year.get_or_create_group_element_year(parent, child_branch=child)

    @property
    def errors(self):
        errors = {}
        for form in self.forms.values():
            errors.update(form.errors)
        return errors


class EducationGroupTypeForm(forms.Form):
    name = forms.ModelChoiceField(EducationGroupType.objects.none(), label=_("training_type"), required=True)

    def __init__(self, parent, category, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["name"].queryset = find_authorized_types(
            category=category,
            parents=parent
        )

        self.fields["name"].label = _("Which type of %(category)s do you want to create ?") % {
            "category": _(category)
        }
