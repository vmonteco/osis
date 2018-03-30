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

from base.forms.bootstrap import BootstrapForm
from base.forms.utils.choice_field import add_blank
from base.models.campus import find_main_campuses, Campus
from base.models.entity_version import find_main_entities_version, EntityVersion
from base.models.enums.learning_container_year_types import LEARNING_CONTAINER_YEAR_TYPES, \
    LEARNING_CONTAINER_YEAR_TYPES_MUST_HAVE_SAME_ENTITIES
from base.models.enums.learning_container_year_types import LEARNING_CONTAINER_YEAR_TYPES_FOR_FACULTY
from base.models.enums.learning_unit_management_sites import LearningUnitManagementSite
from base.models.learning_container_year import LearningContainerYear
from base.models.learning_unit import LEARNING_UNIT_ACRONYM_REGEX_FULL, LearningUnit
from base.models.learning_unit_year import LearningUnitYear
from reference.models import language

MINIMUM_CREDITS = 0
MAXIMUM_CREDITS = 500
MAX_RECORDS = 1000
READONLY_ATTR = "disabled"
PARTIM_FORM_READ_ONLY_FIELD = {'first_letter', 'acronym', 'common_title', 'common_title_english', 'requirement_entity',
                               'allocation_entity', 'language', 'periodicity', 'campus', 'academic_year',
                               'container_type', 'internship_subtype',
                               'additional_requirement_entity_1', 'additional_requirement_entity_2'}


class AcronymInput(forms.MultiWidget):
    template_name = 'learning_unit/blocks/widget/acronym_widget.html'

    def __init__(self, *args, **kwargs):
        choices = kwargs.pop('choices', [])

        widgets = (
            forms.Select(choices=choices),
            forms.TextInput(),
        )
        super().__init__(widgets, *args, **kwargs)

    def decompress(self, value):
        if value:
            return [value[0], value[1:]]
        return [None, None]


class AcronymField(forms.MultiValueField):
    widget = AcronymInput

    def __init__(self, *args, **kwargs):
        max_length = kwargs.pop('max_length')
        list_fields = [
            forms.ChoiceField(choices=_create_first_letter_choices()),
            forms.CharField(max_length=max_length)
        ]
        super().__init__(list_fields, *args, **kwargs)
        self.widget = AcronymInput(choices=_create_first_letter_choices())

    def compress(self, data_list):
        return ''.join(data_list)


def _create_first_letter_choices():
    return add_blank(LearningUnitManagementSite.choices())


def _create_learning_container_year_type_list():
    return add_blank(LEARNING_CONTAINER_YEAR_TYPES)


def _create_faculty_learning_container_type_list():
    return add_blank(LEARNING_CONTAINER_YEAR_TYPES_FOR_FACULTY)


def _merge_first_letter_and_acronym(first_letter, acronym):
    merge_first_letter_acronym = (first_letter + acronym).upper()
    return merge_first_letter_acronym


class EntitiesVersionChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.acronym


class LearningUnitModelForm(forms.ModelForm):
    class Meta:
        model = LearningUnit
        fields = ('acronym', 'title', 'periodicity', 'faculty_remark', 'other_remark')
        field_classes = {
            'acronym': AcronymField
        }


class LearningUnitYearModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.initial.get('subtype') == "PARTIM":
            self.fields['specific_title'].label = _('official_title_proper_to_partim')
            self.fields['specific_title_english'].label = _('official_english_title_proper_to_partim')

    class Meta:
        model = LearningUnitYear
        fields = ('academic_year', 'acronym', 'specific_title', 'specific_title_english', 'subtype', 'credits',
                  'session', 'quadrimester', 'status', 'internship_subtype')
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

    class Meta:
        model = LearningContainerYear
        fields = ('container_type', 'common_title', 'common_title_english', 'language', 'campus')

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

class LearningUnitFormContainer:

    def __init__(self, data, person, academic_year):
        self.learning_unit_year_form = LearningUnitYearModelForm(data, initial={'academic_year': academic_year})
        self.learning_unit_form = LearningUnitModelForm(data)
        self.learning_container_form = LearningContainerYearModelForm(
            data, person, initial={'language': language.find_by_code('FR')})

    def is_valid(self):
        forms_is_valid = [
            self.learning_unit_year_form.is_valid(),
            self.learning_unit_form.is_valid(),
            self.learning_container_form.is_valid()
        ]
        if all(forms_is_valid):
            return self.post_validation()
        return False

    def post_validation(self):
        common_title = self.learning_container_form.cleaned_data["common_title"]
        specific_title = self.learning_unit_year_form.cleaned_data["specific_title"]
        if not common_title and not specific_title:
            self.learning_container_form.add_error("common_title", _("must_set_common_title_or_specific_title"))

    def save(self, commit=True):
        with transaction.atomic():
            self.learning_unit_year_form.save(commit),
            self.learning_unit_form.save(commit),
            self.learning_container_form.save(commit)

    def get_context(self):
        return {'learning_unit_form': self.learning_unit_form,
                'learning_unit_year_form': self.learning_unit_year_form,
                'learning_container_form': self.learning_container_form}


# FIXME Convert it in ModelForm !
class LearningUnitYearForm(BootstrapForm):
    pass


class CreateLearningUnitYearForm(LearningUnitYearForm):


    def clean_acronym(self, regex=LEARNING_UNIT_ACRONYM_REGEX_FULL):
        return super().clean_acronym(regex)


class CreatePartimForm(CreateLearningUnitYearForm):
    # TODO Create widget for partim acronym
    partim_character = forms.CharField(required=True,
                                       widget=forms.TextInput(attrs={'class': 'text-center',
                                                                     'style': 'text-transform: uppercase;',
                                                                     'maxlength': "1",
                                                                     'id': 'hdn_partim_character',
                                                                     'onchange': 'validate_acronym()'}))

    def __init__(self, learning_unit_year_parent, *args, **kwargs):
        self.learning_unit_year_parent = learning_unit_year_parent
        super(CreatePartimForm, self).__init__(*args, **kwargs)
        self.fields['container_type'].choices = _create_learning_container_year_type_list()
        # The credit of LUY partim cannot be greater than credit of full LUY
        self.set_read_only_fields()

    def set_read_only_fields(self):
        for field in PARTIM_FORM_READ_ONLY_FIELD:
            if self.fields.get(field):
                self.fields[field].widget.attrs[READONLY_ATTR] = READONLY_ATTR

