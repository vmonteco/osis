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
    LearningContainerModelForm, EntityContainerFormset, LearningContainerYearModelForm
from django.db import transaction
from django.utils.translation import ugettext_lazy as _

from base.business.learning_units.edition import duplicate_learning_unit_year
from base.models.academic_year import compute_max_academic_year_adjournment, AcademicYear
from base.models.campus import find_main_campuses, Campus
from base.models.enums.component_type import LECTURING, PRACTICAL_EXERCISES
from base.models.enums.entity_container_year_link_type import ENTITY_TYPE_LIST
from base.models.enums.learning_container_year_types import LEARNING_CONTAINER_YEAR_TYPES, \
    LEARNING_CONTAINER_YEAR_TYPES_MUST_HAVE_SAME_ENTITIES, CONTAINER_TYPE_WITH_DEFAULT_COMPONENT
from base.models.enums import learning_unit_year_subtypes
from base.models.learning_unit_year import LearningUnitYear
from reference.models import language
import abc


PARTIM_FORM_READ_ONLY_FIELD = {'common_title', 'common_title_english', 'requirement_entity',
                               'allocation_entity', 'language', 'periodicity', 'campus', 'academic_year',
                               'container_type', 'internship_subtype',
                               'additional_requirement_entity_1', 'additional_requirement_entity_2'}
#
# DEFAULT_ACRONYM_COMPONENT = {
#     LECTURING: "CM1",
#     PRACTICAL_EXERCISES: "TP1",
#     None: "NT1"
# }


class LearningUnitBaseForm:

    forms = [LearningUnitModelForm, LearningUnitYearModelForm, LearningContainerModelForm,
             LearningContainerYearModelForm, EntityContainerFormset]

    form_instances = {}

    subtype = None

    def __init__(self, instances_data, *args, **kwargs):
        for form_class in self.forms:
            self.form_instances[form_class] = form_class(*args, **instances_data[form_class])

    @abc.abstractmethod
    def is_valid(self):
        return False

    @abc.abstractmethod
    def save(self):
        pass

    @property
    def errors(self):
        return [form.errors for form in self.forms]

    @property
    def cleaned_data(self):
        return [form.cleaned_data for form in self.forms]

    def disable_fields(self, field_names):
        for key, value in self.get_all_fields().items():
            value.disabled = key in field_names

    def get_all_fields(self):
        fields = {}
        for cls, form_instance in self.form_instances.items():
            if cls == EntityContainerFormset:
                for index, form in enumerate(form_instance.forms):
                    fields.update({ENTITY_TYPE_LIST[index].lower(): form.fields['entity']})
            else:
                fields.update(form_instance.fields)
        return fields

    def get_context(self):
        return {
            'subtype': self.subtype,
            'learning_unit_form': self.form_instances[LearningUnitModelForm],
            'learning_unit_year_form': self.form_instances[LearningUnitYearModelForm],
            'learning_container_year_form': self.form_instances[LearningContainerYearModelForm],
            'entity_container_form': self.form_instances[EntityContainerFormset]
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
        if instance and not isinstance(instance, LearningUnitYear):
            raise AttributeError('instance arg should be an instance of {}'.format(LearningUnitYear))

        self.academic_year = instance.academic_year if instance else default_ac_year
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
                'initial': {
                    'status': True, 'academic_year': default_ac_year, 'subtype': self.subtype
                } if not instance else None,
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
                } if not instance else None,
                'person': person
            },
            EntityContainerFormset: {
                'data': data,
                'instance': instance.learning_container_year if instance else None,
                'form_kwargs': {'person': person}
            }
        }
        super(FullForm, self).__init__(instances_data, *args, **kwargs)

    def is_valid(self):
        if any([not form_instance.is_valid() for form_instance in self.form_instances.values()]):
            return False
        common_title = self.form_instances[LearningContainerYearModelForm].cleaned_data["common_title"]
        return self._validate_no_empty_title(common_title) and self._validate_same_entities_container()

    def _validate_same_entities_container(self):
        container_type = self.form_instances[LearningContainerYearModelForm].cleaned_data["container_type"]
        requirement_entity = self.form_instances[EntityContainerFormset][0].cleaned_data["entity"]
        allocation_entity = self.form_instances[EntityContainerFormset][1].cleaned_data["entity"]
        if container_type in LEARNING_CONTAINER_YEAR_TYPES_MUST_HAVE_SAME_ENTITIES:
            if requirement_entity != allocation_entity:
                self.form_instances[EntityContainerFormset][1].add_error(
                    "entity", _("requirement_and_allocation_entities_cannot_be_different"))
                return False
        return True

    @transaction.atomic
    def save(self, commit=True):
        academic_year = self.academic_year

        learning_container = self.form_instances[LearningContainerModelForm].save(commit)

        # Save learning unit
        self.form_instances[LearningUnitModelForm].instance.learning_container = learning_container
        self.form_instances[LearningUnitModelForm].instance.start_year = academic_year.year
        learning_unit = self.form_instances[LearningUnitModelForm].save(commit)

        # Save learning container year
        learning_container_form = self.form_instances[LearningContainerYearModelForm]
        learning_container_form.instance.learning_container = learning_container
        learning_container_form.instance.acronym = self.form_instances[LearningUnitYearModelForm].instance.acronym
        learning_container_form.instance.academic_year = academic_year
        learning_container_year = learning_container_form.save(commit)

        # Save entity container year
        self.form_instances[EntityContainerFormset].instance = learning_container_year
        entity_container_years = self.form_instances[EntityContainerFormset].save(commit)

        # Save learning unit year (learning_unit_component +  learning_component_year + entity_component_year)
        self.form_instances[LearningUnitYearModelForm].instance.learning_container_year = learning_container_year
        self.form_instances[LearningUnitYearModelForm].instance.learning_unit = learning_unit
        self.form_instances[LearningUnitYearModelForm].instance.subtype = self.subtype
        learning_unit_year = self.form_instances[LearningUnitYearModelForm].save(commit, entity_container_years)

        return self._make_postponement(learning_unit_year)


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
                'data': _merge_two_dicts(data, inherit_luy_values) if data else None,
                'instance': instance,
                'initial': _merge_two_dicts({'subtype': self.subtype}, inherit_luy_values),
                'person': person,
                'subtype': self.subtype
            },
            LearningContainerYearModelForm: {
                'instance': self.learning_unit_year_full.learning_container_year,
                'person': person
            },
            EntityContainerFormset: {
                'instance': self.learning_unit_year_full.learning_container_year,
                'form_kwargs': {'person': person}
            }
        }
        super(PartimForm, self).__init__(instances_data, *args, **kwargs)
        self.disable_fields(PARTIM_FORM_READ_ONLY_FIELD)

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

    def is_valid(self):
        form_cls_to_validate = [LearningUnitModelForm, LearningUnitYearModelForm]
        if any(not form_instance.is_valid() for cls, form_instance in self.form_instances.items()
               if cls in form_cls_to_validate):
            return False

        common_title = self.learning_unit_year_full.learning_container_year.common_title
        return self._validate_no_empty_title(common_title)

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


def _merge_two_dicts(dict_a, dict_b):
    form_data = dict(dict_a)
    for key in dict_b.keys():
        form_data[key] = dict_b[key]
    return form_data
