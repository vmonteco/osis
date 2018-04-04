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
from django.forms import inlineformset_factory
from django.utils.translation import ugettext_lazy as _

from base.business.learning_units.edition import duplicate_learning_unit_year
from base.forms.utils.acronym_field import AcronymField, PartimAcronymField
from base.forms.utils.choice_field import add_blank
from base.models.academic_year import compute_max_academic_year_adjournment, AcademicYear
from base.models.campus import find_main_campuses, Campus
from base.models.entity_component_year import EntityComponentYear
from base.models.entity_container_year import EntityContainerYear, find_requirement_entities
from base.models.entity_version import find_main_entities_version, get_last_version
from base.models.enums.component_type import LECTURING, PRACTICAL_EXERCISES
from base.models.enums.entity_container_year_link_type import REQUIREMENT_ENTITY, ALLOCATION_ENTITY, \
    ADDITIONAL_REQUIREMENT_ENTITY_1, ADDITIONAL_REQUIREMENT_ENTITY_2, ENTITY_TYPE_LIST, REQUIREMENT_ENTITIES
from base.models.enums.learning_container_year_types import LEARNING_CONTAINER_YEAR_TYPES, \
    LEARNING_CONTAINER_YEAR_TYPES_MUST_HAVE_SAME_ENTITIES, CONTAINER_TYPE_WITH_DEFAULT_COMPONENT
from base.models.enums.learning_container_year_types import LEARNING_CONTAINER_YEAR_TYPES_FOR_FACULTY
from base.models.enums import learning_unit_year_subtypes
from base.models.learning_component_year import LearningComponentYear
from base.models.learning_container import LearningContainer
from base.models.learning_container_year import LearningContainerYear
from base.models.learning_unit import LearningUnit
from base.models.learning_unit_component import LearningUnitComponent
from base.models.learning_unit_year import LearningUnitYear
from reference.models import language

PARTIM_FORM_READ_ONLY_FIELD = {'common_title', 'common_title_english', 'requirement_entity',
                               'allocation_entity', 'language', 'periodicity', 'campus', 'academic_year',
                               'container_type', 'internship_subtype',
                               'additional_requirement_entity_1', 'additional_requirement_entity_2'}

DEFAULT_ACRONYM_COMPONENT = {
    LECTURING: "CM1",
    PRACTICAL_EXERCISES: "TP1",
    None: "NT1"
}


def _get_default_components_type(component_type):
    """This function will return the default components type to create/update according to container type"""
    if component_type in CONTAINER_TYPE_WITH_DEFAULT_COMPONENT:
        return [LECTURING, PRACTICAL_EXERCISES]
    return [None]


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
        widgets = {
            'faculty_remark': forms.Textarea(attrs={'rows': '5'}),
            'other_remark': forms.Textarea(attrs={'rows': '5'})
        }


class LearningContainerModelForm(forms.ModelForm):
    class Meta:
        model = LearningContainer
        fields = ()


class LearningUnitYearModelForm(forms.ModelForm):
    def __init__(self, data, person, *args, **kwargs):
        super().__init__(data, *args, **kwargs)
        if person.is_faculty_manager():
            self.fields.pop('internship_subtype')

    class Meta:
        model = LearningUnitYear
        fields = ('academic_year', 'acronym', 'specific_title', 'specific_title_english', 'credits',
                  'session', 'quadrimester', 'status', 'internship_subtype', 'attribution_procedure')
        widgets = {'subtype': forms.HiddenInput()}
        field_classes = {
            'acronym': AcronymField
        }

    def save(self, commit=True, entity_container_years=list()):
        instance = super().save(commit)
        components_type = _get_default_components_type(self.instance.learning_container_year.container_type)
        for component_type in components_type:
            # Create learning component year
            component, created = LearningComponentYear.objects.get_or_create(
                learning_container_year=instance.learning_container_year,
                type=component_type,
                defaults={'acronym': DEFAULT_ACRONYM_COMPONENT[component_type]}
            )
            # Create learning unit component (Link learning unit year / learning component year)
            LearningUnitComponent.objects.get_or_create(learning_unit_year=instance, learning_component_year=component,
                                                        type=component_type)
            # Create entity component year for requirement entities
            self.create_entity_component_year(component, entity_container_years)
        return instance

    def create_entity_component_year(self, component, entity_container_years):
        requirement_entity_containers = filter(lambda ec: ec.type in REQUIREMENT_ENTITIES, entity_container_years)
        for requirement_entity_container in requirement_entity_containers:
            EntityComponentYear.objects.get_or_create(entity_container_year=requirement_entity_container,
                                                      learning_component_year=component)


class LearningUnitYearPartimModelForm(LearningUnitYearModelForm):
    class Meta(LearningUnitYearModelForm.Meta):
        labels = {
            'specific_title': _('official_title_proper_to_partim'),
            'specific_title_english': _('official_english_title_proper_to_partim')
        }
        field_classes = {
            'acronym': PartimAcronymField
        }


class EntityContainerYearModelForm(forms.ModelForm):
    entity = EntitiesVersionChoiceField(find_main_entities_version())

    def __init__(self, *args, **kwargs):
        entity_type = kwargs.pop('entity_type')
        person = kwargs.pop('person')
        super().__init__(*args, **kwargs)

        self.instance.type = entity_type
        if entity_type == REQUIREMENT_ENTITY:
            self.set_requirement_entity(person)
        elif entity_type == ALLOCATION_ENTITY:
            self.set_allocation_entity()
        elif entity_type == ADDITIONAL_REQUIREMENT_ENTITY_1:
            self.set_additional_requirement_entity_1()
        elif entity_type == ADDITIONAL_REQUIREMENT_ENTITY_2:
            self.set_additional_requirement_entity_2()

        self.fields['entity'].label = _(entity_type.lower())

        if hasattr(self.instance, 'entity'):
            self.initial['entity'] = get_last_version(self.instance.entity)

    def set_requirement_entity(self, person):
        field = self.fields['entity']
        # TODO Really slow method : disabled for the moment
        # field.queryset = person.find_main_entities_version
        field.widget.attrs = {
            'onchange': (
                'updateAdditionalEntityEditability(this.value, "id_additional_requirement_entity_1", false);'
                'updateAdditionalEntityEditability(this.value, "id_additional_requirement_entity_2", true);'
            ), 'id': 'id_requirement_entity'}

    def set_allocation_entity(self):
        field = self.fields['entity']
        field.widget.attrs = {'id': 'allocation_entity'}

    def set_additional_requirement_entity_1(self):
        field = self.fields['entity']
        field.required = False
        field.widget.attrs = {
            'onchange':
                'updateAdditionalEntityEditability(this.value, "id_additional_requirement_entity_2", false)',
                'disable': 'disable',
                'id': 'id_additional_requirement_entity_1'
            }

    def set_additional_requirement_entity_2(self):
        field = self.fields['entity']
        field.required = False
        field.widget.attrs = {'disable': 'disable', 'id': 'id_additional_requirement_entity_2'}

    class Meta:
        model = EntityContainerYear
        fields = ['entity']

    def clean_entity(self):
        return self.cleaned_data['entity'].entity

    def save(self, commit=True):
        if hasattr(self.instance, 'entity'):
            return super().save(commit)


class EntityContainerYearFormset(forms.BaseInlineFormSet):
    def get_form_kwargs(self, index):
        kwargs = super().get_form_kwargs(index)
        instance = kwargs.get('instance')
        if not instance:
            kwargs['entity_type'] = ENTITY_TYPE_LIST[index]
        return kwargs


EntityContainerFormset = inlineformset_factory(
    LearningContainerYear, EntityContainerYear, form=EntityContainerYearModelForm,
    formset=EntityContainerYearFormset, max_num=4, min_num=2, extra=4, can_delete=False
)


class LearningContainerYearModelForm(forms.ModelForm):
    def __init__(self, data, person, *args, **kwargs):
        super().__init__(data, *args, **kwargs)

        self.fields['campus'].queryset = find_main_campuses()
        self.fields['container_type'].widget.attrs ={'onchange': 'showInternshipSubtype()'}

        if person.is_faculty_manager():
            self.fields["container_type"].choices = _create_faculty_learning_container_type_list()

        if self.initial.get('subtype') == learning_unit_year_subtypes.PARTIM:
            self.fields["container_type"].choices = _create_learning_container_year_type_list()

    class Meta:
        model = LearningContainerYear
        fields = ('container_type', 'common_title', 'common_title_english', 'language', 'campus',
                  'type_declaration_vacant', 'team', 'is_vacant')


class LearningUnitFormContainer:
    def __init__(self, data, person, subtype, initial=None, learning_container_year=None, instance=None):
        self.subtype = subtype

        if initial is None:
            initial = {}
        initial.update(self.get_preselected_value())

        learning_container = None
        learning_unit = None
        if instance:
            learning_unit = instance.learning_unit
            learning_container_year = instance.learning_container_year
            learning_container = learning_container_year.learning_container

        self.learning_container_form = LearningContainerModelForm(data, initial=initial, instance=learning_container)
        self.learning_unit_form = LearningUnitModelForm(data, initial=initial, instance=learning_unit)
        # luy_form = LearningUnitYearPartimModelForm if is_partim else LearningUnitYearModelForm
        luy_form = LearningUnitYearModelForm
        self.learning_unit_year_form = luy_form(data, person, initial=initial, instance=instance)
        self.learning_container_year_form = LearningContainerYearModelForm(
            data, person, initial=initial, instance=learning_container_year)
        self.entity_container_form = EntityContainerFormset(data, instance=learning_container_year,
                                                            form_kwargs={'person': person})

        self.forms = [
            self.learning_unit_form, self.learning_container_form,
            self.learning_container_year_form, self.learning_unit_year_form,
            self.entity_container_form
        ]

        if self.subtype == learning_unit_year_subtypes.PARTIM:
            self.disabled_fields()

    def is_valid(self):
        if all(form.is_valid() for form in self.forms):
            return self.post_validation()
        return False

    def post_validation(self):
        result = True
        common_title = self.learning_container_year_form.cleaned_data["common_title"]
        container_type = self.learning_container_year_form.cleaned_data["container_type"]
        specific_title = self.learning_unit_year_form.cleaned_data["specific_title"]
        if not common_title and not specific_title:
            self.learning_container_year_form.add_error("common_title", _("must_set_common_title_or_specific_title"))
            result = False

        requirement_entity = self.entity_container_form.forms[0].cleaned_data["entity"]
        allocation_entity = self.entity_container_form.forms[1].cleaned_data["entity"]

        if container_type in LEARNING_CONTAINER_YEAR_TYPES_MUST_HAVE_SAME_ENTITIES:
            if requirement_entity != allocation_entity:
                self.entity_container_form.forms[1].add_error(
                    "entity", _("requirement_and_allocation_entities_cannot_be_different"))
                result = False
        return result

    @transaction.atomic
    def save(self, commit=True):
        academic_year = self.learning_unit_year.academic_year

        # Save learning container
        learning_container = self.learning_container_form.save(commit)

        # Save learning unit
        self.learning_unit.learning_container = learning_container
        self.learning_unit.start_year = academic_year.year
        learning_unit = self.learning_unit_form.save(commit)

        # Save learning container year
        self.learning_container_year.learning_container = learning_container
        self.learning_container_year.acronym = self.learning_unit_year.acronym
        self.learning_container_year.academic_year = academic_year
        learning_container_year = self.learning_container_year_form.save(commit)

        # Save entity container year
        self.entity_container_form.instance = learning_container_year
        entity_container_years = self.entity_container_form.save(commit)

        # Save learning unit year (learning_unit_component +  learning_component_year + entity_component_year)
        self.learning_unit_year.learning_container_year = learning_container_year
        self.learning_unit_year.learning_unit = learning_unit
        self.learning_unit_year.subtype = self.subtype
        learning_unit_year = self.learning_unit_year_form.save(commit, entity_container_years)

        # Make Postponement
        new_luys = [learning_unit_year]
        for ac_year in range(learning_unit.start_year+1, compute_max_academic_year_adjournment()+1):
            new_luys.append(duplicate_learning_unit_year(new_luys[0], AcademicYear.objects.get(year=ac_year)))
        return new_luys

    def get_context(self):
        return {
            'subtype': self.subtype,
            'learning_unit_form': self.learning_unit_form,
            'learning_unit_year_form': self.learning_unit_year_form,
            'learning_container_year_form': self.learning_container_year_form,
            'entity_container_form': self.entity_container_form
        }

    def disabled_fields(self):
        for key, value in self.all_fields().items():
            if key in PARTIM_FORM_READ_ONLY_FIELD:
                value.disabled = True

    def all_fields(self):
        fields = self.learning_unit_form.fields
        fields.update(self.learning_container_year_form.fields)
        fields.update(self.learning_unit_year_form.fields)
        return fields

    def get_preselected_value(self):
        return {
            # Default campus selected 'Louvain-la-Neuve' if exist
            'campus': Campus.objects.filter(name='Louvain-la-Neuve').first(),
            # Default language French
            'language': language.find_by_code('FR'),
            # Default active UE
            'status': True
        }

    @property
    def errors(self):
        return [form.errors for form in self.forms]

    @property
    def cleaned_data(self):
        return [form.cleaned_data for form in self.forms]

    @property
    def learning_unit(self):
        return self.learning_unit_form.instance

    @property
    def learning_container_year(self):
        return self.learning_container_year_form.instance

    @property
    def learning_unit_year(self):
        return self.learning_unit_year_form.instance
