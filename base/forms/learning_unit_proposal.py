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
from collections import OrderedDict
from itertools import chain

from django import forms
from django.db import transaction

from base.business.learning_unit_proposal import reinitialize_data_before_proposal, compute_proposal_type
from base.business.learning_units.proposal.common import compute_proposal_state
from base.forms.learning_unit.learning_unit_create import EntitiesVersionChoiceField
from base.forms.learning_unit.learning_unit_create_2 import FullForm, PartimForm
from base.models import entity_container_year
from base.models.academic_year import current_academic_year
from base.models.entity_version import find_main_entities_version, get_last_version, get_last_version_by_entity_id
from base.models.enums import entity_container_year_link_type, learning_unit_year_subtypes
from base.models.enums.entity_container_year_link_type import ENTITY_TYPE_LIST
from base.models.enums.proposal_type import ProposalType
from base.models.proposal_learning_unit import ProposalLearningUnit


class ProposalLearningUnitForm(forms.ModelForm):
    # TODO entity must be EntitiesChoiceField
    entity = EntitiesVersionChoiceField(queryset=find_main_entities_version())

    def __init__(self, data, person, *args, initial=None, **kwargs):
        super().__init__(data, *args, **kwargs)

        if initial:
            for key, value in initial.items():
                setattr(self.instance, key, value)

        if hasattr(self.instance, 'entity'):
            self.initial['entity'] = get_last_version(self.instance.entity)

        self.person = person
        if self.person.is_central_manager():
            self.enable_field('state')
        else:
            self.disable_field('state')
        self.disable_field('type')

    def disable_field(self, field):
        self.fields[field].disabled = True
        self.fields[field].required = False

    def enable_field(self, field):
        self.fields[field].disabled = False
        self.fields[field].required = True

    def clean_entity(self):
        return self.cleaned_data['entity'].entity

    class Meta:
        model = ProposalLearningUnit
        fields = ['entity', 'folder_id', 'state', 'type']

    def save(self, commit=True):
        # When we save a creation_proposal, we do not need to save the initial_data
        if hasattr(self.instance, 'learning_unit_year'):
            if self.instance.initial_data:
                reinitialize_data_before_proposal(self.instance)

            self.instance.initial_data = _copy_learning_unit_data(self.instance.learning_unit_year)
        return super().save(commit)


class ProposalBaseForm:
    #Default values
    proposal_type = ProposalType.TRANSFORMATION.name

    def __init__(self, data, person, learning_unit_year, proposal=None, proposal_type=None, default_ac_year=None):
        self.person = person
        self.learning_unit_year = learning_unit_year
        self.proposal = proposal
        if proposal_type:
            self.proposal_type = proposal_type

        initial = self._get_initial()

        if not learning_unit_year or learning_unit_year.subtype == learning_unit_year_subtypes.FULL:
            self.learning_unit_form_container = FullForm(data, person, default_ac_year, instance=learning_unit_year,
                                                         proposal=True)
        else:
            self.learning_unit_form_container = PartimForm(data, person,
                                                      learning_unit_year_full=learning_unit_year.parent,
                                                      instance=learning_unit_year,
                                                      proposal=True)

        self.form_proposal = ProposalLearningUnitForm(data, person=person, instance=proposal,
                                                 initial=initial)

    def is_valid(self):
        return all([self.learning_unit_form_container.is_valid() and self.form_proposal.is_valid()])

    @property
    def errors(self):
        return self.learning_unit_form_container.errors + [self.form_proposal.errors]

    @property
    def fields(self):
        return OrderedDict(chain(self.form_proposal.fields.items(), self.learning_unit_form_container.fields.items()))

    @transaction.atomic
    def save(self):
        proposal = self.form_proposal.save(False)
        proposal.type = compute_proposal_type(self.learning_unit_form_container.cleaned_data, proposal.initial_data)
        proposal = self.form_proposal.save()

        self.learning_unit_form_container.save()
        return proposal

    def _get_initial(self):
        initial = {
                'learning_unit_year': self.learning_unit_year,
                'type': self.proposal_type,
                'state': compute_proposal_state(self.person),
                'author': self.person
        }
        if self.proposal:
            initial['type'] = self.proposal.type
        return initial

    def get_context(self):
        context = self.learning_unit_form_container.get_context()
        context['learning_unit_year'] = self.learning_unit_year
        context['experimental_phase'] = True
        context['person'] = self.person
        context['form_proposal'] = self.form_proposal
        return context


class CreationProposalBaseForm(ProposalBaseForm):
    def __init__(self, data, person, default_ac_year=None):
        if not default_ac_year:
            default_ac_year = current_academic_year()

        super().__init__(data, person, None, proposal_type=ProposalType.CREATION.name,
                         default_ac_year=default_ac_year)

    @transaction.atomic
    def save(self):
        new_luys = self.learning_unit_form_container.save(postponement=False)
        self.form_proposal.instance.learning_unit_year = new_luys[0]
        return self.form_proposal.save()


# # FIXME Split LearningUnitYearForm and ProposalLearningUnit
# class ProposalForm(FullForm):
#     # def __init__(self, data, person, *args, instance=None, **kwargs):
#     #     super().__init__(data, *args, **kwargs)
#     #     self.proposal = instance
#     #
#     #     self.fields["academic_year"].disabled = True
#     #     self.fields["academic_year"].required = False
#     #     self.fields["subtype"].required = False
#     #     When we submit a proposal, we can select all requirement entity available
#     #     self.fields["requirement_entity"].queryset = find_main_entities_version()
#     #     self.person = person
#     #     if self.person.is_central_manager():
#     #         self.fields['state'].disabled = False
#     #         self.fields['state'].required = True
#
#     # def clean(self):
#     #     cleaned_data = super().clean()
#     #     # TODO Move this section in clean_internship_subtype
#     #
#     #     if cleaned_data.get("internship_subtype") and cleaned_data.get("internship_subtype") != 'None' and \
#     #        cleaned_data["container_type"] != learning_container_year_types.INTERNSHIP:
#     #         self.add_error("internship_subtype", _("learning_unit_type_is_not_internship"))
#     #
#     #     return cleaned_data
#
#     # def save(self, learning_unit_year, type_proposal, state_proposal):
#     #     # initial_data = _copy_learning_unit_data(learning_unit_year)
#     #     # learning_container_year = learning_unit_year.learning_container_year
#     #     #
#     #     # _update_model_object(learning_unit_year.learning_unit, self.cleaned_data, ["periodicity"])
#     #     # _update_model_object(learning_unit_year, self.cleaned_data, ["acronym", "status", "quadrimester",
#     #     #                                                              "specific_title", "specific_title_english",
#     #     #                                                              "internship_subtype", "credits"])
#     #     # _update_model_object(learning_container_year, self.cleaned_data, ["acronym", "title", "language", "campus",
#     #     #                                                                   "common_title", "common_title_english",
#     #     #                                                                   "container_type"])
#     #
#     #     # self._updates_entities(learning_container_year)
#     #
#     #     # TODO Move this section in ProposalLearningUnitForm
#     #     # data = {'person': self.person, 'learning_unit_year': learning_unit_year, 'state_proposal': state_proposal,
#     #     #         'type_proposal': type_proposal, 'folder_entity': self.cleaned_data["entity"],
#     #     #         'folder_id': self.cleaned_data['folder_id']}
#     #     if self.proposal:
#     #         if self.proposal.type in \
#     #                 (proposal_type.ProposalType.CREATION.value, proposal_type.ProposalType.SUPPRESSION.value):
#     #             data["type_proposal"] = self.proposal.type
#     #         edition.update_learning_unit_proposal(data, self.proposal)
#     #     else:
#     #         data.update({'initial_data': initial_data})
#     #         creation.create_learning_unit_proposal(data)
#
#     # @cached_property
#     # def changed_data_for_fields_that_can_be_modified(self):
#     #     fields_that_cannot_be_modified = {"academic_year", "subtype", "faculty_remark", "other_remark", "entity",
#     #                                       "folder_id", "state", "type", "session"}
#     #     return list(set(self.changed_data) - fields_that_cannot_be_modified)
#     #
#     # def _updates_entities(self, learning_container_year):
#     #     for entity_type in ENTITY_TYPE_LIST:
#     #         _update_or_delete_entity_container(self.cleaned_data[entity_type.lower()], learning_container_year,
#     #                                            entity_type)


def _copy_learning_unit_data(learning_unit_year):
    learning_container_year = learning_unit_year.learning_container_year
    entities_by_type = entity_container_year.find_entities_grouped_by_linktype(learning_container_year)

    learning_container_year_values = _get_attributes_values(learning_container_year,
                                                            ["id", "acronym", "common_title", "common_title_english",
                                                             "container_type",
                                                             "campus__id", "language__pk", "in_charge"])
    learning_unit_values = _get_attributes_values(learning_unit_year.learning_unit, ["id", "periodicity", "end_year"])
    learning_unit_year_values = _get_attributes_values(learning_unit_year, ["id", "acronym", "specific_title",
                                                                            "specific_title_english",
                                                                            "internship_subtype", "quadrimester",
                                                                            "status"])
    learning_unit_year_values["credits"] = float(learning_unit_year.credits) if learning_unit_year.credits else None
    return get_initial_data(entities_by_type, learning_container_year_values, learning_unit_values,
                            learning_unit_year_values)

#
# def _update_model_object(obj, data_values, fields_to_update):
#     obj_new_values = _create_sub_dictionary(data_values, fields_to_update)
#     _set_attributes_from_dict(obj, obj_new_values)
#     obj.save()


# def _update_or_delete_entity_container(entity_version, learning_container_year, type_entity):
#     if not entity_version:
#         _delete_entity(learning_container_year, type_entity)
#     else:
#         update_or_create_entity_container_year_with_components(entity_version.entity, learning_container_year,
#                                                                type_entity)


# def _delete_entity(learning_container_year, type_entity):
#     an_entity_container_year = entity_container_year.\
#         find_by_learning_container_year_and_linktype(learning_container_year, type_entity)
#     if an_entity_container_year:
#         an_entity_container_year.delete()


# def _set_attributes_from_dict(obj, attributes_values):
#     for key, value in attributes_values.items():
#         setattr(obj, key, value)


# def _create_sub_dictionary(original_dict, list_keys):
#     return {key: value for key, value in original_dict.items() if key in list_keys}


def _get_attributes_values(obj, attributes_name):
    attributes_values = {}
    for attribute_name in attributes_name:
        attributes_hierarchy = attribute_name.split("__")
        value = getattr(obj, attributes_hierarchy[0], None)
        if len(attributes_hierarchy) > 1:
            value = getattr(value, attributes_hierarchy[1], None)
        attributes_values[attributes_hierarchy[0]] = value
    return attributes_values


def get_initial_data(entities_by_type, learning_container_year_values, learning_unit_values, learning_unit_year_values):
    initial_data = {
        "learning_container_year": learning_container_year_values,
        "learning_unit_year": learning_unit_year_values,
        "learning_unit": learning_unit_values,
        "entities": get_entities(entities_by_type)
    }
    return initial_data


def get_entities(entities_by_type):
    return {entity_type: get_entity_by_type(entity_type, entities_by_type) for entity_type in ENTITY_TYPE_LIST}


def get_entity_by_type(entity_type, entities_by_type):
    if entities_by_type.get(entity_type):
        return entities_by_type[entity_type].id
    else:
        return None


# def compute_form_initial_data_from_proposal_json(proposal_initial_data):
#     if not proposal_initial_data:
#         return {}
#     initial_data = {}
#     for value in proposal_initial_data.values():
#         initial_data.update({k.lower(): v for k, v in value.items()})
#     initial_data["first_letter"] = initial_data["acronym"][0]
#     initial_data["acronym"] = initial_data["acronym"][1:]
#     _replace_entity_id_with_entity_version_id(initial_data)
#     return initial_data


# def _replace_entity_id_with_entity_version_id(initial_data):
#     lower_link_types_name = (link_type.lower() for link_type in entity_container_year_link_type.ENTITY_TYPE_LIST)
#     for link_type in lower_link_types_name:
#         entity_id = initial_data.get(link_type)
#         entity_version_id = get_last_version_by_entity_id(entity_id).id if entity_id else None
#         initial_data[link_type] = entity_version_id
