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
from base.models.entity_component_year import EntityComponentYear
from base.models.entity_container_year import EntityContainerYear
from base.models.enums import entity_container_year_link_type, learning_container_year_types, \
    learning_component_year_type
from base.models.learning_component_year import LearningComponentYear
from base.models.learning_container_year import LearningContainerYear
from base.models.learning_unit import LearningUnit
from base.models.learning_unit_component import LearningUnitComponent
from base.models.learning_unit_year import LearningUnitYear

DEFAULT_ACRONYM_LECTURING_COMPONENT = "CM1"
DEFAULT_ACRONYM_PRACTICAL_COMPONENT = "TP1"
UNTYPED_ACRONYM = "NT1"


def create_learning_unit_year_structure(data, new_learning_container, new_learning_unit, academic_year):
    new_learning_container_yr = LearningContainerYear.objects.create(academic_year=academic_year,
                                                                     learning_container=new_learning_container,
                                                                     common_title=data['common_title'],
                                                                     acronym=data['acronym'].upper(),
                                                                     container_type=data['container_type'],
                                                                     language=data['language'],
                                                                     campus=data['campus'],
                                                                     common_title_english=data['common_title_english'])
    # Create Allocation Entity container
    _create_entity_container_year(data['allocation_entity'], new_learning_container_yr,
                                  entity_container_year_link_type.ALLOCATION_ENTITY)

    # Create All Requirements Entity Container [Min 1, Max 3]
    requirement_entity_containers = [_create_entity_container_year(data['requirement_entity'],
                                                                   new_learning_container_yr,
                                                                   entity_container_year_link_type.REQUIREMENT_ENTITY)]
    if data['additional_requirement_entity_1']:
        _append_requirement_entity_container(data['additional_requirement_entity_1'], new_learning_container_yr,
                                             requirement_entity_containers,
                                             entity_container_year_link_type.ADDITIONAL_REQUIREMENT_ENTITY_1)
    if data['additional_requirement_entity_2']:
        _append_requirement_entity_container(data['additional_requirement_entity_2'], new_learning_container_yr,
                                             requirement_entity_containers,
                                             entity_container_year_link_type.ADDITIONAL_REQUIREMENT_ENTITY_2)

    return create_learning_unit_content({'academic_year': academic_year, 'data': data, 'status': data['status'],
                                         'new_learning_container_year': new_learning_container_yr,
                                         'new_learning_unit': new_learning_unit,
                                         'requirement_entity_containers': requirement_entity_containers})


def _append_requirement_entity_container(additional_requirement_entity, new_learning_container_yr,
                                         requirement_entity_containers, link_type):
    requirement_entity_containers.append(_create_entity_container_year(
        additional_requirement_entity, new_learning_container_yr, link_type))


def create_learning_unit(data, learning_container, year, end_year=None):
    return LearningUnit.objects.create(acronym=data['acronym'].upper(), title=data['common_title'], start_year=year,
                                       periodicity=data['periodicity'], learning_container=learning_container,
                                       faculty_remark=data['faculty_remark'], other_remark=data['other_remark'],
                                       end_year=end_year)


def _create_entity_container_year(entity_version, learning_container_year, type_entity_container_year):
    return EntityContainerYear.objects.create(entity=entity_version.entity,
                                              learning_container_year=learning_container_year,
                                              type=type_entity_container_year)


def create_learning_unit_content(data_dict):
    """
    This function will create component + learning unit year according to container_type
    :param data_dict:
    :return: The Learning Unit Year created
    """
    data = data_dict.get('data', None)
    container_type_with_default_component = [learning_container_year_types.COURSE,
                                             learning_container_year_types.MASTER_THESIS,
                                             learning_container_year_types.OTHER_COLLECTIVE,
                                             learning_container_year_types.INTERNSHIP]
    if data['container_type'] in container_type_with_default_component:
        return create_with_lecturing_and_practical_components(data_dict)

    return create_with_untyped_component(data_dict)


def create_with_lecturing_and_practical_components(data_dict):
    new_learning_container_year = data_dict.get('new_learning_container_year', None)
    requirement_entity_containers = data_dict.get('requirement_entity_containers', [])
    new_lecturing = create_learning_component_year(new_learning_container_year,
                                                   DEFAULT_ACRONYM_LECTURING_COMPONENT,
                                                   learning_component_year_type.LECTURING)
    new_practical_exercise = create_learning_component_year(new_learning_container_year,
                                                            DEFAULT_ACRONYM_PRACTICAL_COMPONENT,
                                                            learning_component_year_type.PRACTICAL_EXERCISES)
    for requirement_entity_container in requirement_entity_containers:
        EntityComponentYear.objects.create(entity_container_year=requirement_entity_container,
                                           learning_component_year=new_lecturing)
        EntityComponentYear.objects.create(entity_container_year=requirement_entity_container,
                                           learning_component_year=new_practical_exercise)
    new_learning_unit_year = create_learning_unit_year(data_dict)
    _create_learning_unit_component(new_learning_unit_year, new_lecturing,
                                    learning_component_year_type.LECTURING)
    _create_learning_unit_component(new_learning_unit_year, new_practical_exercise,
                                    learning_component_year_type.PRACTICAL_EXERCISES)
    return new_learning_unit_year


def create_with_untyped_component(data_dict):
    new_learning_container_year = data_dict.get('new_learning_container_year', None)
    requirement_entity_containers = data_dict.get('requirement_entity_containers', [])
    new_learning_component_year = create_learning_component_year(new_learning_container_year, UNTYPED_ACRONYM, None)
    for requirement_entity_container in requirement_entity_containers:
        EntityComponentYear.objects.create(entity_container_year=requirement_entity_container,
                                           learning_component_year=new_learning_component_year)
    new_learning_unit_year = create_learning_unit_year(data_dict)
    _create_learning_unit_component(new_learning_unit_year, new_learning_component_year, None)
    return new_learning_unit_year


def create_learning_component_year(learning_container_year, acronym, type_learning_component_year):
    return LearningComponentYear.objects.create(learning_container_year=learning_container_year,
                                                acronym=acronym,
                                                type=type_learning_component_year)


def create_learning_unit_year(data_dict):
    data = data_dict.get('data')
    return LearningUnitYear.objects.create(academic_year=data_dict.get('academic_year'),
                                           learning_unit=data_dict.get('new_learning_unit'),
                                           learning_container_year=data_dict.get('new_learning_container_year'),
                                           acronym=data['acronym'].upper(),
                                           specific_title=data.get('specific_title'),
                                           specific_title_english=data.get('specific_title_english'),
                                           subtype=data['subtype'],
                                           credits=data['credits'],
                                           internship_subtype=data.get('internship_subtype'),
                                           status=data_dict.get('status'),
                                           session=data['session'],
                                           quadrimester=data['quadrimester'])


def _create_learning_unit_component(learning_unit_year, learning_component_year, type_learning_unit_component):
    return LearningUnitComponent.objects.create(learning_unit_year=learning_unit_year,
                                                learning_component_year=learning_component_year,
                                                type=type_learning_unit_component)
