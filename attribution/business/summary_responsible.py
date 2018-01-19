##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2018 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.core.exceptions import PermissionDenied

from attribution import models as mdl_attr
from attribution.models.attribution import search_by_learning_unit_this_year

from base import models as mdl_base
from base.models.entity_manager import find_entities_with_descendants_from_entity_managers


def get_learning_unit_year_managed_by_user_from_request(request):
    user = request.user
    a_learning_unit_year = _get_learning_unit_year_from_request(request)
    if _is_user_manager_of_entity_allocation_of_learning_unit_year(user, a_learning_unit_year):
        return a_learning_unit_year
    raise PermissionDenied("User is not an entity manager of the allocation entity of the learning unit.")


def _is_user_manager_of_entity_allocation_of_learning_unit_year(user, a_learning_unit_year):
    entities_manager = mdl_base.entity_manager.find_by_user(user)
    entities_with_descendants = find_entities_with_descendants_from_entity_managers(entities_manager)
    return a_learning_unit_year.allocation_entity in entities_with_descendants


def _get_learning_unit_year_from_request(request):
    learning_unit_year_id = request.GET.get('learning_unit_year').strip('learning_unit_year_')
    a_learning_unit_year = mdl_base.learning_unit_year.get_by_id(learning_unit_year_id)
    return a_learning_unit_year


def find_attributions_based_on_request_criterias(entities_manager, request):
    entities_with_descendants = find_entities_with_descendants_from_entity_managers(entities_manager)
    learning_unit_year_attributions_queryset = search_by_learning_unit_this_year(request.GET.get('course_code'),
                                                                                 request.GET.get('learning_unit_title'))
    attributions = list(mdl_attr.attribution.filter_attributions(
        attributions_queryset=learning_unit_year_attributions_queryset,
        entities=entities_with_descendants,
        tutor=request.GET.get('tutor'),
        responsible=request.GET.get('summary_responsible')
    ))
    return attributions
