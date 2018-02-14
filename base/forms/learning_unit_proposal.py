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
from django.utils.translation import ugettext_lazy as _

from base.forms.learning_unit_create import EntitiesVersionChoiceField, LearningUnitYearForm
from base.models import proposal_folder, proposal_learning_unit, entity_container_year
from base.models.entity_version import find_main_entities_version
from base.models.enums import learning_container_year_types
from base.models.enums.entity_container_year_link_type import REQUIREMENT_ENTITY, ALLOCATION_ENTITY, \
    ADDITIONAL_REQUIREMENT_ENTITY_1, ADDITIONAL_REQUIREMENT_ENTITY_2, ENTITY_TYPE_LIST
from django.forms.models import model_to_dict


CSS_SAME_VALUES = {'style': 'border: none;background-color: transparent;cursor: default;'}
CSS_DIFFERENT_VALUES = {'style': 'border: none;background-color: transparent;color:red;cursor: help;'}


def add_none_choice(choices):
    return ((None, "-----"),) + choices


class LearningUnitProposalModificationForm(LearningUnitYearForm):
    folder_entity = EntitiesVersionChoiceField(queryset=find_main_entities_version())
    folder_id = forms.IntegerField(min_value=0)

    def __init__(self, *args, **kwargs):
        super(LearningUnitProposalModificationForm, self).__init__(*args, **kwargs)
        self.fields["academic_year"].disabled = True
        self.fields["academic_year"].required = False
        self.fields["subtype"].required = False
        # When we submit a proposal, we can select all requirement entity available
        self.fields["requirement_entity"].queryset = find_main_entities_version()

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data.get("internship_subtype") and cleaned_data.get("internship_subtype") != 'None' and \
           cleaned_data["container_type"] != learning_container_year_types.INTERNSHIP:
            self.add_error("internship_subtype", _("learning_unit_type_is_not_internship"))

        return cleaned_data

    def save(self, learning_unit_year, a_person, type_proposal, state_proposal):
        if not self.is_valid():
            raise ValueError("Form is invalid.")

        initial_data = _copy_learning_unit_data(learning_unit_year)

        learning_container_year = learning_unit_year.learning_container_year

        _update_model_object(learning_unit_year.learning_unit, self.cleaned_data, ["periodicity"])
        _update_model_object(learning_unit_year, self.cleaned_data, ["acronym", "status", "quadrimester",
                                                                     "internship_subtype", "credits"])
        learning_container_year.common_title = self.cleaned_data['common_title']
        learning_container_year.common_title_english = self.cleaned_data.get('common_title_english')
        _update_model_object(learning_container_year, self.cleaned_data, ["acronym", "title", "language", "campus",
                                                                          "container_type"])

        _update_entity(self.cleaned_data["requirement_entity"], learning_container_year, REQUIREMENT_ENTITY)
        _update_entity(self.cleaned_data["allocation_entity"], learning_container_year, ALLOCATION_ENTITY)
        _update_entity(self.cleaned_data["additional_requirement_entity_1"], learning_container_year,
                       ADDITIONAL_REQUIREMENT_ENTITY_1)
        _update_entity(self.cleaned_data["additional_requirement_entity_2"], learning_container_year,
                       ADDITIONAL_REQUIREMENT_ENTITY_2)

        folder_entity = self.cleaned_data['folder_entity'].entity
        folder_id = self.cleaned_data['folder_id']

        _create_learning_unit_proposal(a_person, folder_entity, folder_id, initial_data, learning_unit_year,
                                       state_proposal, type_proposal)


def _copy_learning_unit_data(learning_unit_year):
    learning_container_year = learning_unit_year.learning_container_year
    entities_by_type = entity_container_year.find_entities_grouped_by_linktype(learning_container_year)

    learning_container_year_values = _get_attributes_values(learning_container_year,
                                                            ["id", "acronym", "common_title", "common_title_english",
                                                             "container_type",
                                                             "campus__id", "language__id", "in_charge"])
    learning_unit_values = _get_attributes_values(learning_unit_year.learning_unit, ["id", "periodicity"])
    learning_unit_year_values = _get_attributes_values(learning_unit_year, ["id", "acronym", "specific_title",
                                                                            "specific_title_english",
                                                                            "internship_subtype", "quadrimester"])
    learning_unit_year_values["credits"] = float(learning_unit_year.credits) if learning_unit_year.credits else None
    return get_initial_data(entities_by_type, learning_container_year_values, learning_unit_values,
                            learning_unit_year_values)


def _update_model_object(obj, data_values, fields_to_update):
    obj_new_values = _create_sub_dictionary(data_values, fields_to_update)
    _set_attributes_from_dict(obj, obj_new_values)
    obj.save()


def _update_entity(entity_version, learning_container_year, type_entity):
    if not entity_version:
        return
    entity_container_year.EntityContainerYear.objects.update_or_create(type=type_entity,
                                                                       learning_container_year=learning_container_year,
                                                                       defaults={"entity": entity_version.entity})


def _create_learning_unit_proposal(a_person, folder_entity, folder_id, initial_data, learning_unit_year,
                                   state_proposal, type_proposal):
    folder, created = proposal_folder.ProposalFolder.objects.get_or_create(entity=folder_entity, folder_id=folder_id)

    proposal_learning_unit.ProposalLearningUnit.objects.create(folder=folder, learning_unit_year=learning_unit_year,
                                                               type=type_proposal, state=state_proposal,
                                                               initial_data=initial_data, author=a_person)


def _set_attributes_from_dict(obj, attributes_values):
    for key, value in attributes_values.items():
        setattr(obj, key, value)


def _create_sub_dictionary(original_dict, list_keys):
    return {key: value for key, value in original_dict.items() if key in list_keys}


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


class LearningUnitProposalViewForm(LearningUnitYearForm):

    def __init__(self, *args, **kwargs):

        luy_proposal_data = kwargs.pop("proposal_data")
        proposal_entities = kwargs.pop("proposal_entities")

        initial = kwargs.get("initial", None)
        learning_unit_year_old = kwargs.pop('learning_unit_year_old')
        learning_container_year_old = kwargs.pop('learning_container_year_old')
        learning_unit_old = kwargs.pop('learning_unit_old')
        modified_data = kwargs.pop('modified_data')

        entities = kwargs.pop('entities')
        old_learning_unit_values = _get_old_values(learning_container_year_old,
                                                   learning_unit_year_old,
                                                   learning_unit_old,
                                                   entities)
        recent_proposal_values = _get_proposal_values(luy_proposal_data, proposal_entities)

        super(LearningUnitProposalViewForm, self).__init__(*args, **kwargs)
        print('++++++++++++++++++++++++')
        print(recent_proposal_values)
        print('++++++++++++++++++++++++')
        print(old_learning_unit_values)
        # print('modified_data')
        # print(modified_data)
        # mod = modified_data.get('learning_unit_year')
        # mod.update(modified_data.get('learning_unit'))
        # mod.update(modified_data.get('learning_container_year'))
        # print(mod)
        if not _all_fields_expected_present(self.fields):
            raise ValueError(
                'Learning_unit_proposal problem'
            )

        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({'readonly': True,
                                                    'disabled': True})
            self.fields[field].widget.attrs.update(CSS_SAME_VALUES)

            recent_value = recent_proposal_values.get(field, None)
            old_value = old_learning_unit_values.get(field, None)

            if recent_value != old_value:
                self.fields[field].widget.attrs.update(CSS_DIFFERENT_VALUES)
                if old_value:
                    self.fields[field].widget.attrs.update({'title': '{} : {}'
                                                           .format(_('value_before_proposal'), old_value)})
                else:
                    self.fields[field].widget.attrs.update({'title': _('no_value_before_proposal')})
            else:
                print('nonononnnonono {}'.format(field))
            # if field in mod:
            #     self.fields[field].widget.attrs.update(CSS_DIFFERENT_VALUES)
                # if old_learning_unit_values.get(field):
                #     self.fields[field].widget.attrs.update\
                #         ({'title': '{} : {}'.format(_('value_before_proposal'),
                #                                     old_learning_unit_values.get(field))})
                # else:
                #     self.fields[field].widget.attrs.update({'title': _('no_value_before_proposal')})


def _get_proposal_values(luy_proposal_data, proposal_entities):
    data_new = model_to_dict(luy_proposal_data)
    data_new.update(model_to_dict(luy_proposal_data.learning_container_year))
    data_new.update(model_to_dict(luy_proposal_data.learning_unit))
    data_new.update(proposal_entities)
    return data_new


def _get_old_values(learning_container_year_old, learning_unit_year_old, learning_unit_old, entities):
    old_data = learning_unit_year_old
    old_data.update(learning_container_year_old)
    old_data.update(learning_unit_old)
    old_data.update({k.lower(): v for k, v in entities.items()})
    return old_data


def _all_fields_expected_present(form_fields):
    field_names_expected = ['acronym', 'status', 'internship_subtype', 'credits', 'common_title',
                            'common_title_english',
                            'subtype', 'container_type', 'periodicity', 'quadrimester', 'requirement_entity',
                            'allocation_entity', 'additional_requirement_entity_1',
                            'additional_requirement_entity_2', 'language']
    for field_name in field_names_expected:
        if field_name not in form_fields:
            return False
    return True
