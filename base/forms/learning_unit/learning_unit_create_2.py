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
from base.forms.learning_unit.learning_unit_create import LearningUnitModelForm, LearningUnitYearModelForm, \
    LearningContainerModelForm, EntityContainerYearFormset, LearningContainerYearModelForm
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
import abc


PARTIM_FORM_READ_ONLY_FIELD = {'common_title', 'common_title_english', 'requirement_entity',
                               'allocation_entity', 'language', 'periodicity', 'campus', 'academic_year',
                               'container_type', 'internship_subtype',
                               'additional_requirement_entity_1', 'additional_requirement_entity_2'}

DEFAULT_ACRONYM_COMPONENT = {
    LECTURING: "CM1",
    PRACTICAL_EXERCISES: "TP1",
    None: "NT1"
}


class LearningUnitBaseForm:

    forms = [LearningUnitModelForm, LearningUnitYearModelForm, LearningContainerModelForm,
             LearningContainerYearModelForm, EntityContainerYearFormset]

    form_instances = {}

    subtype = None

    def __init__(self, *args, **kwargs):
        for form_class in self.forms:
            self.form_instances[form_class] = form_class(*args, **kwargs[form_class])

    def is_valid(self):
        return all([form_instance.is_valid() for form_instance in self.form_instances.values()]) \
               and all([validator(*args) for validator, args in self._get_validators()])

    @abc.abstractmethod
    def save(self):
        pass

    @abc.abstractmethod
    def _get_validators(self):
        return []

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

    def get_context(self):
        return {
            'subtype': self.subtype,
            'learning_unit_form': self.form_instances[LearningUnitModelForm],
            'learning_unit_year_form': self.form_instances[LearningUnitYearModelForm],
            'learning_container_year_form': self.form_instances[LearningContainerYearModelForm],
            'entity_container_form': self.form_instances[EntityContainerYearFormset]
        }

    def _validate_no_empty_title(self, common_title):
        specific_title = self.form_instances[LearningUnitYearModelForm].cleaned_data["specific_title"]
        if not common_title and not specific_title:
            self.form_instances[LearningContainerYearModelForm].add_error("common_title", _("must_set_common_title_or_specific_title"))
            return False
        return True

    def _make_postponement(self, start_luy):
        new_luys = [start_luy]
        for ac_year in range(start_luy.learning_unit.start_year + 1, compute_max_academic_year_adjournment() + 1):
            new_luys.append(duplicate_learning_unit_year(new_luys[0], AcademicYear.objects.get(year=ac_year)))
        return new_luys


class FullForm(LearningUnitBaseForm):

    subtype = learning_unit_year_subtypes.FULL

    def __init__(self, data, person, default_ac_year=None, instance=None, *args, **kwargs):
        if not isinstance(instance, LearningUnitYear):
            raise AttributeError('instance arg should be an instance of {}'.format(LearningUnitYear))

        instances_data = {
            LearningUnitModelForm: {
                'data': data,
                'instance': instance.learning_unit if instance else None,
            },
            LearningContainerModelForm: {
                'data': data,
                'instance': instance.learning_container_year.learning_container if instance else None,
            },
            LearningUnitYearModelForm: {
                'data': data,
                'instance': instance,
                'initial': {'status': True, 'academic_year': default_ac_year, 'subtype': self.subtype},
                'person': person
            },
            LearningContainerYearModelForm: {
                'data': data,
                'instance': instance.learning_container_year if instance else None,
                'initial': {
                    # Default campus selected 'Louvain-la-Neuve' if exist
                    'campus': Campus.objects.filter(name='Louvain-la-Neuve').first(),
                    # Default language French
                    'language': language.find_by_code('FR')
                },
                'person': person
            },
            EntityContainerYearFormset: {
                'data': data,
                'instance': instance.learning_container_year if instance else None,
                'person': person
            }
        }
        kwargs.update(instances_data)
        super().__init__(self, *args, **kwargs)

    def _get_validators(self):
        common_title = self.form_instances[LearningContainerYearModelForm].cleaned_data["common_title"]
        return {
            self._validate_no_empty_title: [common_title],
            self._validate_same_entities_container: [],
        }

    def _validate_same_entities_container(self):
        container_type = self.form_instances[LearningContainerYearModelForm].cleaned_data["container_type"]
        requirement_entity = self.form_instances[EntityContainerYearFormset[0]].cleaned_data["entity"]
        allocation_entity = self.form_instances[EntityContainerYearFormset[1]].cleaned_data["entity"]
        if container_type in LEARNING_CONTAINER_YEAR_TYPES_MUST_HAVE_SAME_ENTITIES:
            if requirement_entity != allocation_entity:
                self.form_instances[EntityContainerYearFormset[1]].add_error(
                    "entity", _("requirement_and_allocation_entities_cannot_be_different"))
                return False
        return True

    @transaction.atomic
    def save(self, commit=True):
        academic_year = self.default_ac_year

        learning_container = self.form_instances[LearningContainerModelForm].save(commit)

        # Save learning unit
        self.form_instances[LearningUnitModelForm].instance.learning_container = learning_container
        self.form_instances[LearningUnitModelForm].instance.start_year = academic_year.year
        learning_unit = self.form_instances[LearningUnitModelForm].save(commit)

        # Save learning container year
        self.form_instances[LearningContainerYearModelForm].instance.learning_container = learning_container
        self.form_instances[LearningContainerYearModelForm].instance.acronym = self.learning_unit_year.acronym
        self.form_instances[LearningContainerYearModelForm].instance.academic_year = academic_year
        learning_container_year = self.form_instances[LearningContainerYearModelForm].save(commit)

        # Save entity container year
        self.form_instances[EntityContainerYearFormset].instance = learning_container_year
        entity_container_years = self.form_instances[EntityContainerYearFormset].save(commit)

        # Save learning unit year (learning_unit_component +  learning_component_year + entity_component_year)
        self.form_instances[LearningUnitYearModelForm].instance.learning_container_year = learning_container_year
        self.form_instances[LearningUnitYearModelForm].instance.learning_unit = learning_unit
        self.form_instances[LearningUnitYearModelForm].instance.subtype = self.subtype
        learning_unit_year = self.form_instances[LearningUnitYearModelForm].save(commit, entity_container_years)

        self._make_postponement(learning_unit_year)



    #
    # def validate_data_between_modelforms(self):
    #     pass


class PartimForm(LearningUnitBaseForm):
    subtype = learning_unit_year_subtypes.PARTIM

    def __init__(self, data, person, learning_unit_year_full, instance=None, *args, **kwargs):
        self.learning_unit_year_full = learning_unit_year_full

        inherit_lu_values = self._get_inherit_learning_unit_full_value()
        inherit_luy_values = self._get_inherit_learning_unit_year_full_value()

        instances_data = {
            LearningUnitModelForm: {
                'data': data,
                'initial': inherit_lu_values,
                'instance': instance.learning_unit if instance else None,
            },
            LearningContainerModelForm: {
                'instance': self.learning_unit_year_full.learning_container_year.learning_container,
            },
            LearningUnitYearModelForm: {
                'data': self._merge_inherit_value(data, inherit_luy_values) if data else None,
                'instance': instance,
                'initial': self._merge_inherit_value({'subtype': self.subtype}, inherit_luy_values),
                'person': person
            },
            LearningContainerYearModelForm: {
                'instance': self.learning_unit_year_full.learning_container_year,
                'person': person
            },
            EntityContainerYearFormset: {
                'instance': self.learning_unit_year_full.learning_container_year,
                'person': person
            }
        }
        kwargs.update(instances_data)
        super().__init__(self, *args, **kwargs)

    def _get_inherit_learning_unit_year_full_value(self):
        """This function will return the inherit value come from learning unit year FULL"""
        return {
            'acronym': self.learning_unit_year_full.acronym,
            'academic_year': self.learning_unit_year_full.academic_year.id,
            'specific_title': self.learning_unit_year_full.specific_title,
            'specific_title_english': self.learning_unit_year_full.specific_title_english,
            'credits': self.learning_unit_year_full.credits,
            'session': self.learning_unit_year_full.session,
            'quadrimester': self.learning_unit_year_full.quadrimester,
            'status': self.learning_unit_year_full.status,
            'internship_subtype': self.learning_unit_year_full.internship_subtype,
            'attribution_procedure': self.learning_unit_year_full.attribution_procedure
        }

    def _get_inherit_learning_unit_full_value(self):
        """This function will return the inherit value come from learning unit FULL"""
        learning_unit_full = self.learning_unit_year_full.learning_unit
        return {
            'periodicity': learning_unit_full.periodicity
        }

    def _merge_inherit_value(self, post_data, inherit_values):
        form_data = dict(inherit_values)
        for key in post_data.keys():
            form_data[key] = post_data[key]
        return form_data

    @transaction.atomic
    def save(self, commit=True):
        # Save learning unit
        learning_unit_instance = self.form_instances[LearningUnitModelForm].instance
        learning_unit_instance.learning_container = self.learning_unit_year_full.learning_container_year.learning_container
        learning_unit_instance.start_year = self.learning_unit_year_full.learning_unit.start_year
        learning_unit = self.form_instances[LearningUnitModelForm].save(commit)

        # Get entity container form full learning container
        learning_container_year_full = self.learning_unit_year_full.learning_container_year
        entity_container_years = learning_container_year_full.entitycontaineryear_set.all()

        # Save learning unit year
        learning_unit_year_instance = self.form_instances[LearningUnitYearModelForm].instance
        learning_unit_year_instance.learning_container_year = learning_container_year_full
        learning_unit_year_instance.learning_unit = learning_unit
        learning_unit_year_instance.subtype = self.subtype
        learning_unit_year = self.form_instances[LearningUnitYearModelForm].save(commit, entity_container_years)

        # Make Postponement
        return self._make_postponement(learning_unit_year)
