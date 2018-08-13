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


# List of key that a user can modify
DATE_FORMAT = '%d-%m-%Y'
DATE_TIME_FORMAT = '%d-%m-%Y %H:%M'
DESC = "desc"
WORKSHEET_TITLE = 'learning_units_comparison'
XLS_FILENAME = 'learning_units_comparison'
XLS_DESCRIPTION = "list_learning_units_comparison"

LEARNING_UNIT_TITLES = [str(_('code')), str(_('academic_year_small')), str(_('type')), str(_('active_title')),
                        str(_('subtype')), str(_('internship_subtype')), str(_('credits')), str(_('language')),
                        str(_('periodicity')),
                        str(_('quadrimester')), str(_('session_title')), str(_('common_title')),
                        str(_('title_proper_to_UE')),
                        str(_('common_english_title')), str(_('english_title_proper_to_UE')),
                        str(_('requirement_entity_small')), str(_('allocation_entity_small')),
                        str(_('additional_requirement_entity_1')), str(_('additional_requirement_entity_2')),
                        str(_('professional_integration')),
                        str(_('institution')),
                        str(_('learning_location'))]


def get_academic_years(luy, acadmic_yr_comparison):
    return luy.academic_year.year, acadmic_yr_comparison


def create_xls(user, learning_unit_years, filters, acadmic_yr_comparison):

    learning_unit_years = LearningUnitYear.objects.filter(learning_unit__in=(_get_learning_units(learning_unit_years)),
                                                          academic_year__year__in=(
                                                          get_academic_years(learning_unit_years[0],
                                                                             acadmic_yr_comparison))).order_by(
        'learning_unit', 'academic_year__year')
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
    print(data)
    return data
    # return [extract_xls_data_from_learning_unit(lu) for lu in found_learning_units]


def extract_xls_data_from_learning_unit(learning_unit_yr, new_line):
    return [
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
        'REQUIREMENT_ENTITY',
        'ALLOCATION_ENTITY',
        'comp1',
        'comp2',
        xls_build.translate(learning_unit_yr.professional_integration),
        'institut',
        learning_unit_yr.campus
    ]


def _translate_status(value):
    if value:
        return _('active').title()
    else:
        return _('inactive').title()
