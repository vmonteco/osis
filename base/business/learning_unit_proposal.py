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
from base.models import entity_container_year
from base.models import campus, entity
from base.models.enums import proposal_type, entity_container_year_link_type
from base.models.proposal_learning_unit import find_by_folder
from reference.models import language
from django.utils.translation import ugettext_lazy as _
from base import models as mdl_base
from django.apps import apps


APP_BASE_LABEL = 'base'
END_FOREIGN_KEY_NAME = "_id"
NO_PREVIOUS_VALUE = '-'
VALUES_WHICH_NEED_TRANSLATION = ["periodicity", "container_type", "internship_subtype"]


def compute_proposal_type(initial_data, current_data):
    data_changed = _compute_data_changed(initial_data, current_data)
    filtered_data_changed = filter(lambda key: key not in ["academic_year", "subtype", "acronym"], data_changed)
    transformation = "{}{}".format(current_data["first_letter"], current_data["acronym"]) != \
                     "{}{}".format(initial_data["first_letter"], initial_data["acronym"])
    modification = any(map(lambda x: x != "acronym", filtered_data_changed))
    if transformation and modification:
        return proposal_type.ProposalType.TRANSFORMATION_AND_MODIFICATION.name
    elif transformation:
        return proposal_type.ProposalType.TRANSFORMATION.name
    return proposal_type.ProposalType.MODIFICATION.name


def _compute_data_changed(initial_data, current_data):
    data_changed = []
    for key, value in initial_data.items():
        current_value = current_data.get(key)
        if str(value) != str(current_value):
            data_changed.append(key)
    return data_changed


def reinitialize_data_before_proposal(learning_unit_proposal, learning_unit_year):
    initial_data = learning_unit_proposal.initial_data
    _reinitialize_model_before_proposal(learning_unit_year, initial_data["learning_unit_year"])
    _reinitialize_model_before_proposal(learning_unit_year.learning_unit, initial_data["learning_unit"])
    _reinitialize_model_before_proposal(learning_unit_year.learning_container_year,
                                        initial_data["learning_container_year"])
    _reinitialize_entities_before_proposal(learning_unit_year.learning_container_year,
                                           initial_data["entities"])


def _reinitialize_model_before_proposal(obj_model, attribute_initial_values):
    for attribute_name, attribute_value in attribute_initial_values.items():
        if attribute_name != "id":
            cleaned_initial_value = _clean_attribute_initial_value(attribute_name, attribute_value)
            setattr(obj_model, attribute_name, cleaned_initial_value)
    obj_model.save()


def _clean_attribute_initial_value(attribute_name, attribute_value):
    clean_attribute_value = attribute_value
    if attribute_name == "campus":
        clean_attribute_value = campus.find_by_id(attribute_value)
    elif attribute_name == "language":
        clean_attribute_value = language.find_by_id(attribute_value)
    return clean_attribute_value


def _reinitialize_entities_before_proposal(learning_container_year, initial_entities_by_type):
    for type_entity, id_entity in initial_entities_by_type.items():
        initial_entity = entity.get_by_internal_id(id_entity)
        if initial_entity:
            entity_container_year.EntityContainerYear.objects.update_or_create(
                learning_container_year=learning_container_year,
                type=type_entity, defaults={"entity": initial_entity})
        else:
            current_entity_container_year = entity_container_year.find_by_learning_container_year_and_linktype(
                learning_container_year, type_entity)
            if current_entity_container_year is not None:
                current_entity_container_year.delete()


def delete_learning_unit_proposal(learning_unit_proposal):
    proposal_folder = learning_unit_proposal.folder
    learning_unit_proposal.delete()
    if not find_by_folder(proposal_folder).exists():
        proposal_folder.delete()


def _get_difference_of_proposal(learning_unit_yr_proposal):
    differences = {}
    if learning_unit_yr_proposal:
        differences.update(_get_differences_in_learning_unit_data(learning_unit_yr_proposal))
        learning_container_yr = mdl_base.learning_container_year \
            .find_by_id(learning_unit_yr_proposal.initial_data.get('learning_container_year').get('id'))
        if learning_container_yr:
            differences.update(_get_difference_of_entity_proposal(learning_container_yr, learning_unit_yr_proposal))

    return differences


def _get_difference_of_entity_proposal(learning_container_yr, learning_unit_yr_proposal):
    differences = {}
    for entity_type, entity_id in learning_unit_yr_proposal.initial_data.get('entities').items():
        entity_cont_yr = mdl_base.entity_container_year \
            .find_by_learning_container_year_and_linktype(learning_container_yr, entity_type)
        if entity_cont_yr:
            differences.update(_get_entity_old_value(entity_cont_yr, entity_id, entity_type))
    return differences


def _get_entity_old_value(entity_cont_yr, entity_id, entity_type):
    differences= {}
    if _has_changed_entity(entity_cont_yr, entity_id):
        old_value = mdl_base.entity.Entity.objects.get(pk=entity_id)
        differences.update({entity_type: "{}".format(old_value.most_recent_acronym)})
    else:
        if entity_type in (entity_container_year_link_type.ADDITIONAL_REQUIREMENT_ENTITY_1,
                           entity_container_year_link_type.ADDITIONAL_REQUIREMENT_ENTITY_2):
            differences.update({entity_type: "{}".format(NO_PREVIOUS_VALUE)})
    return differences


def _has_changed_entity(entity_cont_yr, entity_id):
    if entity_cont_yr.entity.id != entity_id and entity_id:
        return True
    return False


def _get_differences_in_learning_unit_data(learning_unit_yr_proposal):
    learning_unit_yr_initial_data = learning_unit_yr_proposal.initial_data.get('learning_unit_year')
    learning_container_yr_initial_data = learning_unit_yr_proposal.initial_data.get('learning_container_year')
    initial_learning_container_yr_id = learning_container_yr_initial_data.get('id')
    learning_unit_initial_data = learning_unit_yr_proposal.initial_data.get('learning_unit')

    differences = {}
    differences.update(_compare_model_with_initial_value(learning_unit_yr_proposal.learning_unit_year.id,
                                                         learning_unit_yr_initial_data,
                                                         apps.get_model(app_label=APP_BASE_LABEL,
                                                                        model_name="LearningUnitYear")))
    differences.update(_compare_model_with_initial_value(initial_learning_container_yr_id,
                                                         learning_container_yr_initial_data,
                                                         apps.get_model(app_label=APP_BASE_LABEL,
                                                                        model_name="LearningContainerYear")))
    differences.update(_compare_model_with_initial_value(learning_unit_initial_data.get('id'),
                                                         learning_unit_initial_data,
                                                         apps.get_model(app_label=APP_BASE_LABEL,
                                                                        model_name="LearningUnit")))
    return differences


def _compare_model_with_initial_value(an_id, model_initial_data, mymodel):
    differences = {}
    qs = (mymodel.objects.filter(pk=an_id).values())
    if len(qs) > 0:
        differences.update(_check_differences(model_initial_data,
                                              qs[0]))
    return differences


def _replace_key_of_foreign_key(data):
    return {key_name.replace(END_FOREIGN_KEY_NAME, ''): data[key_name] for key_name in data.keys()}


def _check_differences(initial_data, actual_data):
    if initial_data:
        return _compare_initial_actual_data(actual_data, initial_data)
    return {}


def _compare_initial_actual_data(actual_data, initial_data):
    corrected_dict = _replace_key_of_foreign_key(actual_data)
    differences = {}
    for attribute, initial_value in initial_data.items():
        if attribute in corrected_dict and initial_data.get(attribute, None) != corrected_dict.get(attribute):
            differences.update(_get_the_old_value(attribute, actual_data, initial_data))
    return differences


def _get_the_old_value(key, actual_data, initial_data):
    differences = {}

    initial_value = NO_PREVIOUS_VALUE
    if initial_data.get(key):
        initial_value = initial_data.get(key)

    if _is_foreign_key(key, actual_data):
        differences.update(_get_str_representing_old_data_from_foreign_key(key, initial_value))
    else:
        if key in VALUES_WHICH_NEED_TRANSLATION and initial_value != NO_PREVIOUS_VALUE:
            differences.update({key: "{}".format(_(initial_value))})
        else:
            differences.update({key: "{}".format(initial_value)})
    return differences


def _get_str_representing_old_data_from_foreign_key(cle, initial_value):
    if initial_value != NO_PREVIOUS_VALUE:
        return _get_old_value_of_foreign_key(cle, initial_value)
    else:
        return {cle: "{}".format(NO_PREVIOUS_VALUE)}


def _get_old_value_of_foreign_key(cle, initial_value):
    differences = {}
    if cle == 'campus':
        differences.update({cle: "{}".format(mdl_base.campus.find_by_id(initial_value))})
    if cle == 'language':
        differences.update({cle: "{}".format(language.find_by_id(initial_value))})
    return differences


def _is_foreign_key(cle, actual_data):
    if "{}{}".format(cle, END_FOREIGN_KEY_NAME) in actual_data:
        return True
    return False
