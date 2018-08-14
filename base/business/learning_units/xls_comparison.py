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
from django.utils.translation import ugettext_lazy as _

from base.models.learning_unit_year import LearningUnitYear
from osis_common.document import xls_build
from base.business.xls import get_name_or_username
from base.business.learning_unit_year_with_context import append_latest_entities, append_components, \
    get_learning_component_prefetch
from base.business.entity import build_entity_container_prefetch
from base.models.enums import entity_container_year_link_type as entity_types
from base.models.enums import learning_component_year_type
from base.business.learning_unit import get_organization_from_learning_unit_year
from base.business.learning_units.comparison import get_partims_as_str

# List of key that a user can modify
DATE_FORMAT = '%d-%m-%Y'
DATE_TIME_FORMAT = '%d-%m-%Y %H:%M'
DESC = "desc"
WORKSHEET_TITLE = 'learning_units_comparison'
XLS_FILENAME = 'learning_units_comparison'
XLS_DESCRIPTION = "list_learning_units_comparison"

LEARNING_UNIT_TITLES = [str(_('code')), str(_('academic_year_small')), str(_('type')), str(_('active_title')),
                        str(_('subtype')), str(_('Internship subtype')), str(_('credits')), str(_('language')),
                        str(_('periodicity')),
                        str(_('quadrimester')), str(_('session_title')), str(_('common_title')),
                        str(_('title_proper_to_UE')),
                        str(_('common_english_title')), str(_('english_title_proper_to_UE')),
                        str(_('requirement_entity_small')), str(_('allocation_entity_small')),
                        str(_('Add. requ. ent. 1')), str(_('Add. requ. ent. 2')),
                        str(_('Profes. integration')),
                        str(_('institution')),
                        str(_('learning_location')),
                        str(_('partims')),
                        "PM {}".format(_('code')),
                        "PM {}".format(_('volume_partial')),
                        "PM {}".format(_('volume_remaining')),
                        "PM {}".format(_('Vol. annual')),
                        "PM {}".format(_('real_classes')),
                        "PM {}".format(_('planned_classes')),
                        "PM {}".format(_('vol_global')),
                        "PM {}".format(_('requirement_entity')),
                        "PM {}".format(_('Add. requ. ent. 1')),
                        "PM {}".format(_('Add. requ. ent. 2')),
                        "PP {}".format(_('code')),
                        "PP {}".format(_('volume_partial')),
                        "PP {}".format(_('volume_remaining')),
                        "PP {}".format(_('Vol. annual')),
                        "PM {}".format(_('real_classes')),
                        "PM {}".format(_('planned_classes')),
                        "PP {}".format(_('vol_global')),
                        "PP {}".format(_('requirement_entity')),
                        "PM {}".format(_('Add. requ. ent. 1')),
                        "PM {}".format(_('Add. requ. ent. 2'))
                        ]


def get_academic_years(luy, acadmic_yr_comparison):
    return luy.academic_year.year, acadmic_yr_comparison


def create_xls_comparison(user, learning_unit_years, filters, academic_yr_comparison):
    learning_unit_years = LearningUnitYear.objects.filter(learning_unit__in=(_get_learning_units(learning_unit_years)),
                                                          academic_year__year__in=(
                                                          get_academic_years(learning_unit_years[0],
                                                                             academic_yr_comparison)))\
        .select_related('academic_year', 'learning_container_year', 'learning_container_year__academic_year') \
        .prefetch_related(get_learning_component_prefetch()) \
        .prefetch_related(build_entity_container_prefetch([entity_types.ALLOCATION_ENTITY,
                                                           entity_types.REQUIREMENT_ENTITY,
                                                           entity_types.ADDITIONAL_REQUIREMENT_ENTITY_1,
                                                           entity_types.ADDITIONAL_REQUIREMENT_ENTITY_2])) \
        .order_by('learning_unit', 'academic_year__year')
    [append_latest_entities(learning_unit, False) for learning_unit in learning_unit_years]
    [append_components(learning_unit) for learning_unit in learning_unit_years]
    working_sheets_data = prepare_xls_content(learning_unit_years)

    parameters = {xls_build.DESCRIPTION: XLS_DESCRIPTION,
                  xls_build.USER: get_name_or_username(user),
                  xls_build.FILENAME: XLS_FILENAME,
                  xls_build.HEADER_TITLES: LEARNING_UNIT_TITLES,
                  xls_build.WS_TITLE: WORKSHEET_TITLE}

    return xls_build.generate_xls(xls_build.prepare_xls_parameters_list(working_sheets_data, parameters), filters)


def _get_learning_units(learning_unit_years):
    distinct_learning_unit = []
    for l in learning_unit_years:
        if l.learning_unit not in distinct_learning_unit:
            distinct_learning_unit.append(l.learning_unit)
    return distinct_learning_unit


def prepare_xls_content(found_learning_unit_yrs):
    data = []
    lu = None

    for l_u_yr in found_learning_unit_yrs:

        if lu is None:
            lu = l_u_yr.learning_unit
            new_line = True
        else:
            if lu == l_u_yr.learning_unit:
                new_line = False
            else:
                lu = l_u_yr.learning_unit
                new_line = True

        data.append(extract_xls_data_from_learning_unit(l_u_yr, new_line))
    return data
    # return [extract_xls_data_from_learning_unit(lu) for lu in found_learning_units]


def extract_xls_data_from_learning_unit(learning_unit_yr, new_line):
    organization = get_organization_from_learning_unit_year(learning_unit_yr)
    partims = learning_unit_yr.get_partims_related()
    data = [
        learning_unit_yr.acronym if new_line else '',
        learning_unit_yr.academic_year.name,
        xls_build.translate(learning_unit_yr.learning_container_year.container_type),
        _translate_status(learning_unit_yr.status),
        xls_build.translate(learning_unit_yr.subtype),
        str(_(learning_unit_yr.internship_subtype)) if learning_unit_yr.internship_subtype else '',
        learning_unit_yr.credits,
        learning_unit_yr.language.name if learning_unit_yr.language else '',
        str(_(learning_unit_yr.periodicity)) if learning_unit_yr.periodicity else '',
        str(_(learning_unit_yr.quadrimester)) if learning_unit_yr.quadrimester else '',
        str(_(learning_unit_yr.session)) if learning_unit_yr.session else '',
        learning_unit_yr.learning_container_year.common_title,
        learning_unit_yr.specific_title,
        learning_unit_yr.learning_container_year.common_title_english,
        learning_unit_yr.specific_title_english,
        learning_unit_yr.entities.get(entity_types.REQUIREMENT_ENTITY).acronym,
        learning_unit_yr.entities.get(entity_types.ALLOCATION_ENTITY).acronym,
        learning_unit_yr.entities.get(
            entity_types.ADDITIONAL_REQUIREMENT_ENTITY_1).acronym if learning_unit_yr.entities.get(
            entity_types.ADDITIONAL_REQUIREMENT_ENTITY_1) else '',
        learning_unit_yr.entities.get(
            entity_types.ADDITIONAL_REQUIREMENT_ENTITY_2).acronym if learning_unit_yr.entities.get(
            entity_types.ADDITIONAL_REQUIREMENT_ENTITY_2) else '',
        xls_build.translate(learning_unit_yr.professional_integration),
        organization.name if organization else '',
        learning_unit_yr.campus,
        get_partims_as_str(partims),
    ]

    data.extend(_component_data(learning_unit_yr.components, learning_component_year_type.LECTURING))
    data.extend(_component_data(learning_unit_yr.components, learning_component_year_type.PRACTICAL_EXERCISES))
    return data


def _translate_status(value):
    if value:
        return _('active').title()
    else:
        return _('inactive').title()


def _component_data(components, learning_component_yr_type):
    for component in components:
        if component.type == learning_component_yr_type:
            volumes = components[component]
            return [
                component.acronym if component.acronym else '',
                volumes.get('VOLUME_Q1', ''),
                volumes.get('VOLUME_Q2', ''),
                volumes.get('VOLUME_TOTAL', ''),
                component.real_classes if component.real_classes else '',
                component.planned_classes if component.planned_classes else '',
                volumes.get('VOLUME_GLOBAL', '0'),
                volumes.get('VOLUME_REQUIREMENT_ENTITY', ''),
                volumes.get('VOLUME_ADDITIONAL_REQUIREMENT_ENTITY_1', ''),
                volumes.get('VOLUME_ADDITIONAL_REQUIREMENT_ENTITY_2', '')


            ]


