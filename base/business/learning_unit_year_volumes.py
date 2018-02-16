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

from base.business import learning_unit_year_with_context
from base.models import learning_unit_year
from base.models.enums import entity_container_year_link_type as entity_types
from base.models.enums import learning_unit_year_subtypes
from django.utils.translation import ugettext_lazy as _

ENTITY_TYPES = [
    entity_types.REQUIREMENT_ENTITY,
    entity_types.ADDITIONAL_REQUIREMENT_ENTITY_1,
    entity_types.ADDITIONAL_REQUIREMENT_ENTITY_2
]


def update_volumes(learning_unit_year_id, updated_volumes):
    volumes_grouped_by_lunityear = get_volumes_grouped_by_lunityear(learning_unit_year_id, updated_volumes)
    _save(volumes_grouped_by_lunityear)


def get_volumes_grouped_by_lunityear(learning_unit_year_id, updated_volumes):
    # Retrieve value from database
    volumes_grouped_by_lunityear = _get_volumes_from_db(learning_unit_year_id)
    for lunityear in volumes_grouped_by_lunityear:
        # Format str to Decimal
        updated_volume = updated_volumes.get(lunityear.id)
        # Replace volumes database by volumes entered by user
        lunityear.components = _set_volume_to_components(lunityear.components, updated_volume)
    return volumes_grouped_by_lunityear


def _save(volumes_grouped_by_lunityear):
    for lunityear in volumes_grouped_by_lunityear:
        for component, data in lunityear.components.items():
            component.hourly_volume_partial = data.get('VOLUME_Q1')
            component.planned_classes = data.get('PLANNED_CLASSES')
            component.save()
            _save_requirement_entities(component.entity_components_year, data)


def _save_requirement_entities(entity_components_year, data):
    for ecy in entity_components_year:
        link_type = ecy.entity_container_year.type
        ecy.repartition_volume = data.get('VOLUME_' + link_type)
        ecy.save()


def _get_volumes_from_db(learning_unit_year_id):
    luy = learning_unit_year.get_by_id(learning_unit_year_id)
    return learning_unit_year_with_context.get_with_context(
        learning_container_year_id=luy.learning_container_year
    )


def _get_learning_unit_parent(volumes_grouped_by_lunityear):
    return next((lunit_year for lunit_year in volumes_grouped_by_lunityear
                 if lunit_year.subtype == learning_unit_year_subtypes.FULL), None)


def _set_volume_to_components(components, updated_volume):
    if components and updated_volume:
        components_updated = {}
        for component, data in components.items():
            data_updated = updated_volume.get(component.id, {})
            data_updated = dict(data, **data_updated)
            components_updated[component] = _format_volumes(data_updated)
        return components_updated
    return components
