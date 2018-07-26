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
from django.core.exceptions import PermissionDenied
from django.db.models import Prefetch
from django.utils.translation import ugettext_lazy as _

from base.models.entity import Entity
from base.models.enums import academic_calendar_type
from base.models.enums import education_group_categories
from base.models.enums import offer_year_entity_type
from base.models.mandate import Mandate
from base.models.offer_year_calendar import OfferYearCalendar
from base.models.person import Person
from base.models.program_manager import is_program_manager
from base.models import person_entity
from osis_common.document import xls_build
from base.business.xls import get_name_or_username, convert_boolean


# List of key that a user can modify
DATE_FORMAT = '%d-%m-%Y'
DATE_TIME_FORMAT = '%d-%m-%Y %H:%M'
DESC = "desc"
WORKSHEET_TITLE = 'education_groups'
XLS_FILENAME = 'education_groups_filename'
XLS_DESCRIPTION = "list_education_groups"
EDUCATION_GROUP_TITLES = [str(_('academic_year_small')), str(_('code')), str(_('title')), str(_('type')),
                          str(_('entity')), str(_('code'))]
ORDER_COL = 'order_col'
ORDER_DIRECTION = 'order_direction'
#

WORKSHEET_TITLE_ADMINISTRATIVE = 'trainings'
XLS_FILENAME_ADMINISTRATIVE = 'training_administrative_data'
XLS_DESCRIPTION_ADMINISTRATIVE = "List of trainings, with administrative data"

# Column for xls with administrative data
MANAGEMENT_ENTITY_COL = 'management_entity'
TRANING_COL = 'TRAINING'
TYPE_COL = 'type'
ACADEMIC_YEAR_COL = 'academic_year_small'
START_COURSE_REGISTRATION_COL = 'Begining of course registration'
END_COURSE_REGISTRATION_COL = 'Ending of course registration'
START_EXAM_REGISTRATION_COL = 'Begining of exam registration'
END_EXAM_REGISTRATION_COL = 'Ending of exam registration'
MARKS_PRESENTATION_COL = 'marks_presentation'
DISSERTATION_PRESENTATION_COL = 'dissertation_presentation'
DELIBERATION_COL = 'DELIBERATION'
SCORES_DIFFUSION_COL = 'scores_diffusion'
WEIGHTING_COL = 'Weighting'
DEFAULT_LEARNING_UNIT_ENROLLMENT_COL = 'Default learning unit enrollment'
CHAIR_OF_THE_EXAM_BOARD_COL = 'chair_of_the_exam_board'
EXAM_BOARD_SECRETARY_COL = 'exam_board_secretary'
EXAM_BOARD_SIGNATORY_COL = 'Exam board signatory'
SIGNATORY_QUALIFICATION_COL = 'signatory_qualification'

SESSIONS_COLUMNS = 'sessions_columns'
SESSIONS_NUMBER = 3
SESSION_HEADERS = [
    START_EXAM_REGISTRATION_COL,
    END_EXAM_REGISTRATION_COL,
    MARKS_PRESENTATION_COL,
    DISSERTATION_PRESENTATION_COL,
    DELIBERATION_COL,
    SCORES_DIFFUSION_COL
]
EDUCATION_GROUP_TITLES_ADMINISTRATIVE = [
    MANAGEMENT_ENTITY_COL,
    TRANING_COL,
    TYPE_COL,
    ACADEMIC_YEAR_COL,
    START_COURSE_REGISTRATION_COL,
    END_COURSE_REGISTRATION_COL,
    SESSIONS_COLUMNS,   # this columns will be duplicate by SESSIONS_NUMBER [content: SESSION_HEADERS]
    WEIGHTING_COL,
    DEFAULT_LEARNING_UNIT_ENROLLMENT_COL,
    CHAIR_OF_THE_EXAM_BOARD_COL,
    EXAM_BOARD_SECRETARY_COL,
    EXAM_BOARD_SIGNATORY_COL,
    SIGNATORY_QUALIFICATION_COL,
]

SIGNATORIES = 'signatories'
SECRETARIES = 'secretaries'
PRESIDENTS = 'presidents'
NUMBER_SESSIONS = 3


def can_user_edit_administrative_data(a_user, an_education_group_year):
    """
    Edition of administrative data is allowed for user which have permission AND
            if CENTRAL_MANAGER: Check attached entities [person_entity]
            else Check if user is program manager of education group
    """
    if not a_user.has_perm("base.can_edit_education_group_administrative_data"):
        return False

    person = Person.objects.get(user=a_user)
    if person.is_central_manager() and _is_management_entity_linked_to_user(person, an_education_group_year):
        return True

    return is_program_manager(a_user, education_group=an_education_group_year.education_group)


def _is_management_entity_linked_to_user(person, an_education_group_year):
    entities = Entity.objects.filter(offeryearentity__education_group_year=an_education_group_year,
                                     offeryearentity__type=offer_year_entity_type.ENTITY_MANAGEMENT)

    return person_entity.is_attached_entities(person, entities)


def assert_category_of_education_group_year(education_group_year, authorized_categories):
    if education_group_year.education_group_type.category not in authorized_categories:
        raise PermissionDenied("Education group category is not correct.")


def create_xls(user, found_education_groups_param, filters, order_data):
    found_education_groups = ordering_data(found_education_groups_param, order_data)
    working_sheets_data = prepare_xls_content(found_education_groups)
    parameters = {xls_build.DESCRIPTION: XLS_DESCRIPTION,
                  xls_build.USER: get_name_or_username(user),
                  xls_build.FILENAME: XLS_FILENAME,
                  xls_build.HEADER_TITLES: EDUCATION_GROUP_TITLES,
                  xls_build.WS_TITLE: WORKSHEET_TITLE}

    return xls_build.generate_xls(xls_build.prepare_xls_parameters_list(working_sheets_data, parameters), filters)


def prepare_xls_content(found_education_groups):
    return [extract_xls_data_from_education_group(eg) for eg in found_education_groups]


def extract_xls_data_from_education_group(an_education_group):
    return [
        an_education_group.academic_year.name,
        an_education_group.acronym,
        an_education_group.title,
        an_education_group.education_group_type,
        an_education_group.management_entity_version.acronym,
        an_education_group.partial_acronym
    ]


def ordering_data(object_list, order_data):
    order_col = order_data.get(ORDER_COL)
    order_direction = order_data.get(ORDER_DIRECTION)
    reverse_direction = order_direction == DESC

    return sorted(list(object_list), key=lambda t: _get_field_value(t, order_col), reverse=reverse_direction)


def _get_field_value(instance, field):
    field_path = field.split('.')
    attr = instance
    for elem in field_path:
        try:
            attr = getattr(attr, elem) or ''
        except AttributeError:
            return None
    return attr


def create_xls_administrative_data(user, education_group_years_qs, filters, order_data):
    # Make select_related/prefetch_related in order to have low DB HIT
    education_group_years = education_group_years_qs.filter(
        education_group_type__category=education_group_categories.TRAINING
    ).select_related(
        'education_group_type',
        'academic_year',
    ).prefetch_related(
        Prefetch(
            'education_group__mandate_set',
            queryset=Mandate.objects.prefetch_related('mandatary_set')
        ),
        Prefetch(
            'offeryearcalendar_set',
            queryset=OfferYearCalendar.objects.select_related('academic_calendar__sessionexamcalendar')
        )
    )
    found_education_groups = ordering_data(education_group_years, order_data)
    working_sheets_data = prepare_xls_content_administrative(found_education_groups)
    header_titles = _get_translated_header_titles()
    parameters = {
        xls_build.DESCRIPTION: XLS_DESCRIPTION_ADMINISTRATIVE,
        xls_build.USER: get_name_or_username(user),
        xls_build.FILENAME: XLS_FILENAME_ADMINISTRATIVE,
        xls_build.HEADER_TITLES: header_titles,
        xls_build.WS_TITLE: WORKSHEET_TITLE_ADMINISTRATIVE
    }
    return xls_build.generate_xls(xls_build.prepare_xls_parameters_list(working_sheets_data, parameters), filters)


def _get_translated_header_titles():
    translated_hearders = []
    for title in EDUCATION_GROUP_TITLES_ADMINISTRATIVE:
        if title != SESSIONS_COLUMNS:
            translated_hearders.append(str(_(title)))
        else:
            translated_hearders.extend(_get_translated_header_session_columns())
    return translated_hearders


def _get_translated_header_session_columns():
    translated_session_headers = []
    for title in SESSION_HEADERS:
        translated_session_headers.append(str(_(title)))

    # Duplicate translation by nb_session + append nb_session to title
    all_headers_sessions = []
    for session_number in range(1, SESSIONS_NUMBER + 1):
        all_headers_sessions += ["{} {} ".format(translated_title, session_number) for translated_title in
                                  translated_session_headers]
    return all_headers_sessions


def prepare_xls_content_administrative(education_group_years):
    xls_data = []
    for education_group_year in education_group_years:
        main_data = _extract_main_data(education_group_year)
        administrative_data = _extract_administrative_data(education_group_year)
        mandatary_data = _extract_mandatary_data(education_group_year)

        # Put all dict together and ordered it by EDUCATION_GROUP_TITLES_ADMINISTRATIVE
        row = _convert_data_to_xls_row(
            education_group_year_data={**main_data, **administrative_data, **mandatary_data},
            header_list=EDUCATION_GROUP_TITLES_ADMINISTRATIVE
        )
        xls_data.append(row)
    return xls_data


def _extract_main_data(an_education_group_year):
    return {
        MANAGEMENT_ENTITY_COL: an_education_group_year.management_entity_version.acronym,
        TRANING_COL: an_education_group_year.acronym,
        TYPE_COL: an_education_group_year.education_group_type,
        ACADEMIC_YEAR_COL: an_education_group_year.academic_year.name,
        WEIGHTING_COL: convert_boolean(an_education_group_year.weighting),
        DEFAULT_LEARNING_UNIT_ENROLLMENT_COL: convert_boolean(an_education_group_year.default_learning_unit_enrollment)
    }


def _extract_administrative_data(an_education_group_year):
    course_enrollment_calendar = _get_offer_year_calendar_from_prefetched_data(
        an_education_group_year,
        academic_calendar_type.COURSE_ENROLLMENT
    )
    administrative_data = {
        START_COURSE_REGISTRATION_COL: _format_date(course_enrollment_calendar, 'start_date'),
        END_COURSE_REGISTRATION_COL: _format_date(course_enrollment_calendar, 'end_date'),
        SESSIONS_COLUMNS: [
            _extract_session_data(an_education_group_year, session_number) for
                session_number in range(1, SESSIONS_NUMBER + 1)
        ]
    }
    return administrative_data


def _extract_session_data(education_group_year, session_number):
    session_academic_cal_type = [
        academic_calendar_type.EXAM_ENROLLMENTS,
        academic_calendar_type.SCORES_EXAM_SUBMISSION,
        academic_calendar_type.DISSERTATION_SUBMISSION,
        academic_calendar_type.DELIBERATION,
        academic_calendar_type.SCORES_EXAM_DIFFUSION
    ]
    academic_cals = {}
    for academic_cal_type in session_academic_cal_type:
        academic_cals[academic_cal_type] = _get_academic_calendar_from_prefetched_data(
            education_group_year,
            academic_cal_type,
            session_number
        )
    #@Todo: Fix correct date format
    return {
        START_EXAM_REGISTRATION_COL: _format_date(academic_cals[academic_calendar_type.EXAM_ENROLLMENTS], 'start_date'),
        END_EXAM_REGISTRATION_COL: _format_date(academic_cals[academic_calendar_type.EXAM_ENROLLMENTS], 'end_date'),
        MARKS_PRESENTATION_COL: _format_date(academic_cals[academic_calendar_type.SCORES_EXAM_SUBMISSION], 'start_date'),
        DISSERTATION_PRESENTATION_COL: _format_date(academic_cals[academic_calendar_type.DISSERTATION_SUBMISSION], 'start_date'),
        DELIBERATION_COL: _format_date(academic_cals[academic_calendar_type.DELIBERATION], 'start_date'),
        SCORES_DIFFUSION_COL: _format_date(academic_cals[academic_calendar_type.SCORES_EXAM_DIFFUSION], 'start_date'),
    }


def _extract_mandatary_data(an_education_group_year):
    #@Todo: Add mandatary data
    return {
        CHAIR_OF_THE_EXAM_BOARD_COL: '',
        EXAM_BOARD_SECRETARY_COL: '',
        EXAM_BOARD_SIGNATORY_COL: '',
        SIGNATORY_QUALIFICATION_COL: '',
    }


def _convert_data_to_xls_row(education_group_year_data, header_list):
    xls_row = []
    for header in header_list:
        if header == SESSIONS_COLUMNS:
            session_datas = education_group_year_data.get(header, [])
            xls_row.extend(_convert_session_data_to_xls_row(session_datas))
        else:
            value = education_group_year_data.get(header, '')
            xls_row.append(value)
    return xls_row


def _convert_session_data_to_xls_row(session_datas):
    xls_session_rows = []
    for session_number in range(0, SESSIONS_NUMBER):
        session_formated = _convert_data_to_xls_row(session_datas[session_number], SESSION_HEADERS)
        xls_session_rows.extend(session_formated)
    return xls_session_rows


def _get_offer_year_calendar_from_prefetched_data(an_education_group_year, academic_calendar_type):
    offer_year_cals = _get_all_offer_year_calendar_from_prefetched_data(
        an_education_group_year,
        academic_calendar_type
    )
    return offer_year_cals[0] if offer_year_cals else None


def _get_academic_calendar_from_prefetched_data(an_education_group_year, academic_calendar_type, session_number):
    offer_year_cals = _get_all_offer_year_calendar_from_prefetched_data(
        an_education_group_year,
        academic_calendar_type
    )
    return next((
        offer_year_cal.academic_calendar for offer_year_cal in offer_year_cals
        if offer_year_cal.academic_calendar.session_exam_calendar.number_session == session_number
    ), None)


def _get_all_offer_year_calendar_from_prefetched_data(an_education_group_year, academic_calendar_type):
    return [
        offer_year_calendar for offer_year_calendar in an_education_group_year.offeryearcalendar_set.all()
        if offer_year_calendar.academic_calendar.reference == academic_calendar_type
    ]


def _format_date(obj, date_key):
    date = getattr(obj, date_key, None) if obj else None
    if date:
        return date.strftime(DATE_FORMAT)
    return '-'


# def extract_xls_administrative_data_from_education_group(an_education_group):
#     data = [
#         an_education_group.management_entity_version.acronym,
#         an_education_group.acronym,
#         an_education_group.education_group_type,
#         an_education_group.academic_year.name,
#         _get_date(an_education_group.administrative_data, 'course_enrollment.dates.start_date',
#                   DATE_FORMAT),
#         _get_date(an_education_group.administrative_data, 'course_enrollment.dates.end_date',
#                   DATE_FORMAT)]
#     for session_number in range(NUMBER_SESSIONS):
#         data.extend(_get_dates_by_session(an_education_group.administrative_data, session_number+1))
#     data.extend([
#         convert_boolean(an_education_group.weighting),
#         convert_boolean(an_education_group.default_learning_unit_enrollment),
#         names(an_education_group.administrative_data[PRESIDENTS]),
#         names(an_education_group.administrative_data[SECRETARIES]),
#         names(an_education_group.administrative_data[SIGNATORIES]),
#         qualification(an_education_group.administrative_data[SIGNATORIES])]
#     )
#     return data
#
#
# def names(representatives):
#     return ', '.join([str(mandatory.person) for mandatory in representatives])
#
#
# def qualification(signatories):
#     return ', '.join([signatory.mandate.qualification for signatory in signatories if signatory.mandate.qualification])
#
#
# def _get_date(administrative_data, keys_attribute, date_form):
#     key1, key2, attribute = keys_attribute.split(".")
#
#     if administrative_data[key1].get(key2):
#         attr = getattr(administrative_data[key1].get(key2), attribute) or None
#         if attr:
#             return attr.strftime(date_form)
#     return '-'
#
#
# def _get_dates_by_session(administrative_data, session_number):
#     session_name = "session{}".format(session_number)
#     return (
#         _get_date(administrative_data, "{}.{}.{}".format('exam_enrollments', session_name, 'start_date'), DATE_FORMAT),
#         _get_date(administrative_data, "{}.{}.{}".format('exam_enrollments', session_name, 'end_date'), DATE_FORMAT),
#         _get_date(administrative_data, "{}.{}.{}".format('scores_exam_submission', session_name, 'start_date'),
#                   DATE_TIME_FORMAT),
#         _get_date(administrative_data, "{}.{}.{}".format('dissertation_submission', session_name, 'start_date'),
#                   DATE_FORMAT),
#         _get_date(administrative_data, "{}.{}.{}".format('deliberation', session_name, 'start_date'), DATE_TIME_FORMAT),
#         _get_date(administrative_data, "{}.{}.{}".format('scores_exam_diffusion', session_name, 'start_date'),
#                   DATE_TIME_FORMAT)
#     )
