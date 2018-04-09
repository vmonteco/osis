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
        fields = ('periodicity', 'faculty_remark', 'other_remark', )
        widgets = {
            'faculty_remark': forms.Textarea(attrs={'rows': '5'}),
            'other_remark': forms.Textarea(attrs={'rows': '5'})
        }


class LearningContainerModelForm(forms.ModelForm):
    class Meta:
        model = LearningContainer
        fields = ()


class LearningUnitYearModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        if kwargs.pop('person').is_faculty_manager():
            self.fields.pop('internship_subtype')
        subtype = kwargs.pop('subtype')
        super().__init__(*args, **kwargs)
        if subtype == learning_unit_year_subtypes.PARTIM:
            self.fields['specific_title'].label = _('official_title_proper_to_partim')
            self.fields['specific_title_english'].label = _('official_english_title_proper_to_partim')

        if kwargs.get('instance'):
            self.fields['academic_year'].disabled = True

    class Meta:
        model = LearningUnitYear
        fields = ('academic_year', 'acronym', 'specific_title', 'specific_title_english', 'credits',
                  'session', 'quadrimester', 'status', 'internship_subtype', 'attribution_procedure', 'subtype', )
        widgets = {'subtype': forms.HiddenInput()}
        field_classes = {'acronym': AcronymField}

    def save(self, commit=True, entity_container_years=None):
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

    def create_entity_component_year(self, component, entity_container_years=None):
        if entity_container_years is None:
            entity_container_years = []
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
        entity_version = self.cleaned_data['entity']
        return entity_version.entity if entity_version else None

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
    formset=EntityContainerYearFormset, max_num=4, min_num=3, extra=4, can_delete=False
)


class LearningContainerYearModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        person = kwargs.pop('person')
        super().__init__(*args, **kwargs)

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
    def __init__(self, data, person, default_ac_year=None, learning_unit_year_full=None, instance=None):
        self.learning_unit_year_full = learning_unit_year_full
        self.default_ac_year=default_ac_year

        learning_unit = None
        learning_container = None
        learning_container_year = None
        if instance:
            learning_unit = instance.learning_unit
            learning_container_year = instance.learning_container_year
            learning_container = learning_container_year.learning_container
        elif self.subtype == learning_unit_year_subtypes.PARTIM:
            # If subtype PARTIM, the container come from FULL LUY args
            learning_container_year = learning_unit_year_full.learning_container_year
            learning_container = learning_container_year.learning_container

        self.learning_container_form = self._get_learning_container_form(learning_container, data)
        self.learning_unit_form = self._get_learning_unit_form(self.subtype, learning_unit, data)
        self.learning_unit_year_form = self._get_learning_unit_year_form(self.subtype, instance, person, data)
        self.learning_container_year_form = self._get_learning_container_year_form(
            self.subtype, learning_container_year, person, data)
        self.entity_container_form = self._get_entity_container_formset(self.subtype, learning_container_year, person,
                                                                        data)

        self.forms = [
            self.learning_unit_form, self.learning_container_form,
            self.learning_container_year_form, self.learning_unit_year_form,
            self.entity_container_form
        ]

        if self.subtype == learning_unit_year_subtypes.PARTIM:
            self.disable_fields(PARTIM_FORM_READ_ONLY_FIELD)

    def is_valid(self):
        if self.subtype == learning_unit_year_subtypes.FULL:
            form_list = self.forms
        else:
            form_list = [self.learning_unit_year_form, self.learning_unit_form]
        return all(form.is_valid() for form in form_list) and self._is_valid_between_modelforms()

    def _is_valid_between_modelforms(self):
        if self.subtype == learning_unit_year_subtypes.FULL:
            validations = [self._validate_no_empty_title, self._validate_same_entities_container]
        else:
            validations = [self._validate_no_empty_title]
        return all(validation() for validation in validations)

    def _validate_same_entities_container(self):
        container_type = self.learning_container_year_form.cleaned_data["container_type"]
        requirement_entity = self.entity_container_form.forms[0].cleaned_data["entity"]
        allocation_entity = self.entity_container_form.forms[1].cleaned_data["entity"]
        if container_type in LEARNING_CONTAINER_YEAR_TYPES_MUST_HAVE_SAME_ENTITIES:
            if requirement_entity != allocation_entity:
                self.entity_container_form.forms[1].add_error(
                    "entity", _("requirement_and_allocation_entities_cannot_be_different"))
                return False
        return True

    def _validate_no_empty_title(self):
        if self.subtype == learning_unit_year_subtypes.FULL:
            common_title = self.learning_container_year_form.cleaned_data["common_title"]
        else:
            common_title = self.learning_unit_year_full.learning_container_year.common_title

        specific_title = self.learning_unit_year_form.cleaned_data["specific_title"]
        if not common_title and not specific_title:
            self.learning_container_year_form.add_error("common_title", _("must_set_common_title_or_specific_title"))
            return False
        return True

    @transaction.atomic
    def save(self, commit=True):
        if self.subtype == learning_unit_year_subtypes.FULL:
            return self._save_full(commit)
        else:
            return self._save_partim(commit)

    def _save_full(self, commit):
        academic_year = self.default_ac_year

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
        return self._make_postponement(learning_unit_year)

    def _save_partim(self, commit):
        # Save learning unit
        self.learning_unit.learning_container = self.learning_unit_year_full.learning_container_year.learning_container
        self.learning_unit.start_year = self.learning_unit_year_full.learning_unit.start_year
        learning_unit = self.learning_unit_form.save(commit)

        # Get entity container form full learning container
        learning_container_year_full = self.learning_unit_year_full.learning_container_year
        entity_container_years = learning_container_year_full.entitycontaineryear_set.all()

        # Save learning unit year
        self.learning_unit_year.learning_container_year = learning_container_year_full
        self.learning_unit_year.learning_unit = learning_unit
        self.learning_unit_year.subtype = self.subtype
        learning_unit_year = self.learning_unit_year_form.save(commit, entity_container_years)

        # Make Postponement
        return self._make_postponement(learning_unit_year)

    def _make_postponement(self, start_luy):
        new_luys = [start_luy]
        for ac_year in range(start_luy.learning_unit.start_year + 1, compute_max_academic_year_adjournment() + 1):
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

    def disable_fields(self, field_names):
        for key, value in self.get_all_fields().items():
            value.disabled = key in field_names

    def get_all_fields(self):
        fields = {}
        for form in self.forms:
            if form == self.entity_container_form:
                for index, form in enumerate(self.entity_container_form.forms):
                    fields.update({ENTITY_TYPE_LIST[index].lower(): form.fields['entity']})
            else:
                fields.update(form.fields)
        return fields

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

    @property
    def subtype(self):
        return learning_unit_year_subtypes.PARTIM if self.learning_unit_year_full else \
            learning_unit_year_subtypes.FULL

    def _get_entity_container_formset(self, subtype, learning_container_year, person, post_data):
        form_data = {'instance': learning_container_year, 'form_kwargs': {'person': person}}
        if subtype == learning_unit_year_subtypes.FULL:
            # A partim cannot modify the entities linked (Only FULL LUY CAN)
            form_data['data'] = post_data
        return EntityContainerFormset(**form_data)

    def _get_learning_container_year_form(self, subtype, learning_container_year, person, post_data):
        initial = {
            # Default campus selected 'Louvain-la-Neuve' if exist
            'campus': Campus.objects.filter(name='Louvain-la-Neuve').first(),
            # Default language French
            'language': language.find_by_code('FR')
        }
        form_data = {'person': person, 'instance': learning_container_year, 'initial': initial}
        if subtype == learning_unit_year_subtypes.FULL:
            form_data['data'] = post_data
        return LearningContainerYearModelForm(**form_data)

    def _get_learning_unit_year_form(self, subtype, learning_unit_year, person, post_data):
        initial = {'status': True, 'academic_year': self.default_ac_year, 'subtype': self.subtype}
        form_data = {'person': person, 'instance': learning_unit_year, 'data': post_data, 'initial': initial}
        if subtype == learning_unit_year_subtypes.PARTIM:
            # Get inherit value form full learning unit year
            inherit_values = self._get_inherit_luy_value_from_full()
            form_data['initial'].update(inherit_values)
            if post_data:
                form_data['data'] = self._merge_inherit_value(inherit_values, post_data)
            return LearningUnitYearPartimModelForm(**form_data)
        return LearningUnitYearModelForm(**form_data)

    def _get_learning_unit_form(self, subtype, learning_unit, post_data):
        initial = {}
        if subtype == learning_unit_year_subtypes.PARTIM:
            initial.update(self._get_inherit_lu_value_from_full())
        return LearningUnitModelForm(post_data, instance=learning_unit)

    def _get_learning_container_form(self, learning_container, post_data):
        return LearningContainerModelForm(post_data, instance=learning_container)

    def _get_inherit_luy_value_from_full(self):
        learning_unit_year_full = self.learning_unit_year_full
        return {
            'acronym': learning_unit_year_full.acronym,
            'academic_year': learning_unit_year_full.academic_year.id,
            'specific_title': learning_unit_year_full.specific_title,
            'specific_title_english': learning_unit_year_full.specific_title_english,
            'credits': learning_unit_year_full.credits,
            'session': learning_unit_year_full.session,
            'quadrimester': learning_unit_year_full.quadrimester,
            'status': learning_unit_year_full.status,
            'internship_subtype': learning_unit_year_full.internship_subtype,
            'attribution_procedure': learning_unit_year_full.attribution_procedure
        }

    def _get_inherit_lu_value_from_full(self):
        learning_unit_full = self.learning_unit_year_full.learning_unit
        return {
            'periodicity': learning_unit_full.periodicity
        }

    def _merge_inherit_value(self, inherit_values, post_data):
        form_data = dict(inherit_values)
        for key in post_data.keys():
            form_data[key] = post_data[key]
        return form_data
