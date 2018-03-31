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
from django.db import transaction
from django.utils.translation import ugettext_lazy as _

from base.business.learning_units.edition import duplicate_learning_unit_year
from base.business.learning_units.simple.creation import _create_entity_container_year, \
    _append_requirement_entity_container
from base.forms.utils.choice_field import add_blank
from base.models.academic_year import compute_max_academic_year_adjournment, AcademicYear
from base.models.campus import find_main_campuses, Campus
from base.models.entity_version import find_main_entities_version, EntityVersion
from base.models.enums import entity_container_year_link_type
from base.models.enums.learning_container_year_types import LEARNING_CONTAINER_YEAR_TYPES, \
    LEARNING_CONTAINER_YEAR_TYPES_MUST_HAVE_SAME_ENTITIES
from base.models.enums.learning_container_year_types import LEARNING_CONTAINER_YEAR_TYPES_FOR_FACULTY
from base.models.enums.learning_unit_management_sites import LearningUnitManagementSite
from base.models.learning_container import LearningContainer
from base.models.learning_container_year import LearningContainerYear
from base.models.learning_unit import LearningUnit
from base.models.learning_unit_year import LearningUnitYear
from reference.models import language

PARTIM_FORM_READ_ONLY_FIELD = {'first_letter', 'acronym', 'common_title', 'common_title_english', 'requirement_entity',
                               'allocation_entity', 'language', 'periodicity', 'campus', 'academic_year',
                               'container_type', 'internship_subtype',
                               'additional_requirement_entity_1', 'additional_requirement_entity_2'}


class AcronymInput(forms.MultiWidget):
    template_name = 'learning_unit/blocks/widget/acronym_widget.html'

    def __init__(self, *args, is_partim=False, **kwargs):
        choices = kwargs.pop('choices', [])
        self.is_partim = is_partim
        widgets = [
            forms.Select(choices=choices),
            forms.TextInput(),
        ]

        if self.is_partim:
            widgets.append(
                forms.TextInput(attrs={'class': 'text-center',
                                       'style': 'text-transform: uppercase;',
                                       'maxlength': "1",
                                       'onchange': 'validate_acronym()'})
            )

        super().__init__(widgets, *args, **kwargs)

    def decompress(self, value):
        return self.decompress_partim(value) if self.is_partim else self.decompress_full(value)

    @staticmethod
    def decompress_full(value):
        if value:
            return [value[0], value[1:-1], value[-1]]
        return [None, None, None]

    @staticmethod
    def decompress_partim(value):
        if value:
            return [value[0], value[1:-1], ]


class AcronymField(forms.MultiValueField):
    widget = AcronymInput

    def __init__(self, *args, is_partim=False, **kwargs):
        max_length = kwargs.pop('max_length')
        list_fields = [
            forms.ChoiceField(choices=_create_first_letter_choices()),
            forms.CharField(max_length=max_length)
        ]
        if is_partim:
            list_fields.append(forms.CharField(max_length=1))

        super().__init__(list_fields, *args, **kwargs)
        self.widget = AcronymInput(choices=_create_first_letter_choices(), is_partim=is_partim)

    def compress(self, data_list):
        return ''.join(data_list)


def _create_first_letter_choices():
    return add_blank(LearningUnitManagementSite.choices())


def _create_learning_container_year_type_list():
    return add_blank(LEARNING_CONTAINER_YEAR_TYPES)


def _create_faculty_learning_container_type_list():
    return add_blank(LEARNING_CONTAINER_YEAR_TYPES_FOR_FACULTY)


class EntitiesVersionChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.acronym


class LearningUnitModelForm(forms.ModelForm):
    class Meta:
        model = LearningUnit
        fields = ('periodicity', 'faculty_remark', 'other_remark')


class LearningUnitYearModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.initial.get('subtype') == "PARTIM":
            self.fields['specific_title'].label = _('official_title_proper_to_partim')
            self.fields['specific_title_english'].label = _('official_english_title_proper_to_partim')

            self.fields['acronym'].widget = AcronymField(is_partim=True, max_length=10)

    class Meta:
        model = LearningUnitYear
        fields = ('academic_year', 'acronym', 'specific_title', 'specific_title_english', 'subtype', 'credits',
                  'session', 'quadrimester', 'status', 'internship_subtype', 'attribution_procedure')
        field_classes = {
            'acronym': AcronymField
        }


class LearningContainerYearModelForm(forms.ModelForm):
    requirement_entity = EntitiesVersionChoiceField(EntityVersion.objects.none(),
        widget=forms.Select(
            attrs={
                'onchange': (
                    'updateAdditionalEntityEditability(this.value, "id_additional_requirement_entity_1", false);'
                    'updateAdditionalEntityEditability(this.value, "id_additional_requirement_entity_2", true);'
                )
            }
        )
    )
    allocation_entity = EntitiesVersionChoiceField(
        find_main_entities_version(), widget=forms.Select(attrs={'id': 'allocation_entity'})
    )
    additional_requirement_entity_1 = EntitiesVersionChoiceField(
        find_main_entities_version(), required=False,
        widget=forms.Select(
            attrs={
                'onchange':
                    'updateAdditionalEntityEditability(this.value, "id_additional_requirement_entity_2", false)',
                'disable': 'disable'
            }
        )
    )
    additional_requirement_entity_2 = EntitiesVersionChoiceField(
        queryset=find_main_entities_version(), required=False, widget=forms.Select(attrs={'disable': 'disable'})
    )

    def __init__(self, data, person, *args, **kwargs):
        super().__init__(data, *args, **kwargs)
        self.fields['campus'].queryset = find_main_campuses()

        # TODO the default values must be set in model.
        qs = Campus.objects.filter(name='Louvain-la-Neuve')
        if qs.exists():
            self.fields['campus'].initial = qs.get()

        self.fields['container_type'].widget.attrs ={'onchange': 'showInternshipSubtype()'}

        # When we create a learning unit, we can only select requirement entity which are attached to the person
        self.fields["requirement_entity"].queryset = person.find_main_entities_version
        if person.is_faculty_manager():
            self.fields["container_type"].choices = _create_faculty_learning_container_type_list()
            self.fields.pop('internship_subtype')

        if self.initial.get('subtype') == "PARTIM":
            _create_learning_container_year_type_list()

    class Meta:
        model = LearningContainerYear
        fields = ('container_type', 'common_title', 'common_title_english', 'language', 'campus',
                  'type_declaration_vacant', 'team', 'is_vacant')

    def clean(self):
        cleaned_data = super().clean()
        if self.errors:
            return cleaned_data

        requirement_entity = cleaned_data["requirement_entity"]
        allocation_entity = cleaned_data["allocation_entity"]
        container_type = cleaned_data["container_type"]

        if (requirement_entity != allocation_entity
                and container_type in LEARNING_CONTAINER_YEAR_TYPES_MUST_HAVE_SAME_ENTITIES):
                self.add_error("allocation_entity", _("requirement_and_allocation_entities_cannot_be_different"))
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit)

        # Create Allocation Entity container
        _create_entity_container_year(self.cleaned_data['allocation_entity'],
                                      instance, entity_container_year_link_type.ALLOCATION_ENTITY)

        # Create All Requirements Entity Container [Min 1, Max 3]
        requirement_entity_containers = [
            _create_entity_container_year(self.cleaned_data['requirement_entity'], instance,
                                          entity_container_year_link_type.REQUIREMENT_ENTITY)]

        if self.cleaned_data.get('additional_requirement_entity_1'):
            _append_requirement_entity_container(
                self.data['additional_requirement_entity_1'], instance, requirement_entity_containers,
                entity_container_year_link_type.ADDITIONAL_REQUIREMENT_ENTITY_1
            )

        if self.cleaned_data.get('additional_requirement_entity_2'):
            _append_requirement_entity_container(
                self.cleaned_data['additional_requirement_entity_2'], instance, requirement_entity_containers,
                entity_container_year_link_type.ADDITIONAL_REQUIREMENT_ENTITY_2
            )
        return instance


class LearningUnitFormContainer:

    def __init__(self, data, person, is_partim=False, initial=None, instance=None):
        if initial:
            initial['language'] = language.find_by_code('FR')

        self.learning_unit_year_form = LearningUnitYearModelForm(
            data, initial=initial, instance=instance)
        self.learning_unit_form = LearningUnitModelForm(
            data, initial=initial, instance=instance.learning_unit)
        self.learning_container_form = LearningContainerYearModelForm(
            data, person, initial=initial, instance=instance.learning_container_year)

        self.forms = [self.learning_unit_form, self.learning_container_form, self.learning_unit_year_form]

        if is_partim:
            self.disabled_fields()

    def is_valid(self):
        if all(form.is_valid() for form in self.forms):
            return self.post_validation()
        return False

    def post_validation(self):
        common_title = self.learning_container_form.cleaned_data["common_title"]
        specific_title = self.learning_unit_year_form.cleaned_data["specific_title"]
        if not common_title and not specific_title:
            self.learning_container_form.add_error("common_title", _("must_set_common_title_or_specific_title"))
            return False
        return True

    @transaction.atomic
    def save(self, commit=True):
        learning_container = LearningContainer.objects.create()
        self.assign_duplicated_data(learning_container)

        learning_unit = self.learning_unit_form.save(commit)
        learning_container_year = self.learning_container_form.save(commit)

        # TODO Create components
        self.learning_unit_year.learning_container_year = learning_container_year
        self.learning_unit_year.learning_unit = learning_unit
        new_luys = [self.learning_unit_year_form.save(commit)]

        for ac_year in range(learning_unit.start_year+1, compute_max_academic_year_adjournment()+1):
            new_luys.append(duplicate_learning_unit_year(new_luys[0], AcademicYear.objects.get(year=ac_year)))

        return new_luys

    def assign_duplicated_data(self, learning_container):
        self.learning_unit.learning_container = learning_container
        self.learning_container_year.learning_container = learning_container
        self.learning_container_year.academic_year = self.learning_unit_year.academic_year
        self.learning_unit.start_year = self.learning_unit_year.academic_year.year
        self.learning_unit.acronym = self.learning_unit_year.acronym

    def get_context(self):
        return {'learning_unit_form': self.learning_unit_form,
                'learning_unit_year_form': self.learning_unit_year_form,
                'learning_container_form': self.learning_container_form}

    def disabled_fields(self):
        for key, value in self.all_fields():
            value.required = True

    def all_fields(self):
        fields = self.learning_unit_form.fields
        fields.update(self.learning_container_form.fields)
        fields.udapte(self.learning_unit_year_form.fields)
        return fields

    @property
    def learning_unit(self):
        return self.learning_unit_form.instance

    @property
    def learning_container_year(self):
        return self.learning_container_form.instance

    @property
    def learning_unit_year(self):
        return self.learning_unit_year_form.instance
