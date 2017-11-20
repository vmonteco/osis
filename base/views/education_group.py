##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2017 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required, permission_required
from base import models as mdl

from base.forms.education_groups import EducationGroupFilter, MAX_RECORDS
from base.models.enums import education_group_categories

from . import layout
from cms.enums import entity_name
from cms import models as mdl_cms
from collections import OrderedDict
from django.conf import settings
from base.forms.education_group_general_informations import EducationGroupGeneralInformationsForm
from django.utils import timezone
from base.models.enums import academic_calendar_type


@login_required
@permission_required('base.can_access_offer', raise_exception=True)
def education_groups(request):
    if request.GET:
        form = EducationGroupFilter(request.GET)
    else:
        current_academic_year = mdl.academic_year.current_academic_year()
        form = EducationGroupFilter(initial={'academic_year': current_academic_year,
                                             'category': education_group_categories.TRAINING})

    object_list = None
    if form.is_valid():
        object_list = form.get_object_list()
        if not _check_if_display_message(request, object_list):
            object_list = None

    context = {
        'form': form,
        'object_list': object_list,
        'experimental_phase': True
    }
    return layout.render(request, "education_groups.html", context)


def _check_if_display_message(request, an_education_groups):
    if not an_education_groups:
        messages.add_message(request, messages.WARNING, _('no_result'))
    elif len(an_education_groups) > MAX_RECORDS:
        messages.add_message(request, messages.WARNING, _('too_many_results'))
        return False
    return True


@login_required
@permission_required('base.can_access_offer', raise_exception=True)
def education_group_read(request, education_group_year_id):
    root = request.GET.get('root')
    education_group_year = mdl.education_group_year.find_by_id(education_group_year_id)
    education_group_languages = [education_group_language.language.name for education_group_language in
                                 mdl.education_group_language.find_by_education_group_year(education_group_year)]
    if root:
        parent = mdl.education_group_year.find_by_id(root)
    else:
        parent = education_group_year
    return layout.render(request, "education_group/tab_identification.html", locals())


@login_required
@permission_required('base.can_access_offer', raise_exception=True)
def education_group_parent_read(request, education_group_year_id):
    root = request.GET.get('root')
    education_group_year = mdl.education_group_year.find_by_id(education_group_year_id)
    education_group_languages = [education_group_language.language.name for education_group_language in
                                 mdl.education_group_language.find_by_education_group_year(education_group_year)]
    if root:
        parent = mdl.education_group_year.find_by_id(root)
    else:
        parent = education_group_year
    return layout.render(request, "education_group/tab_identification.html", locals())


@login_required
@permission_required('base.can_access_offer', raise_exception=True)
def education_group_diplomas(request, education_group_year_id):
    return _education_group_diplomas_tab(request, education_group_year_id)


def _education_group_diplomas_tab(request, education_group_year_id):
    education_group_year = mdl.education_group_year.find_by_id(education_group_year_id)
    return layout.render(request, "education_group/tab_diplomas.html", locals())


@login_required
@permission_required('base.can_access_offer', raise_exception=True)
def education_group_general_informations(request, education_group_year_id):
    return _education_group_general_informations_tab(request, education_group_year_id)


def _education_group_general_informations_tab(request, education_group_year_id):
    education_group_year = mdl.education_group_year.find_by_id(education_group_year_id)

    CMS_LABEL = mdl_cms.translated_text.find_by_entity_reference(entity_name.OFFER_YEAR, education_group_year_id)

    fr_language = next((lang for lang in settings.LANGUAGES if lang[0] == 'fr-be'), None)
    en_language = next((lang for lang in settings.LANGUAGES if lang[0] == 'en'), None)

    context = {'education_group_year': education_group_year,
               'cms_labels_translated': _get_cms_label_data(CMS_LABEL,
                                                            mdl.person.get_user_interface_language(request.user)),
               'form_french': EducationGroupGeneralInformationsForm(education_group_year=education_group_year,
                                                                    language=fr_language, text_labels_name=CMS_LABEL),
               'form_english': EducationGroupGeneralInformationsForm(education_group_year=education_group_year,
                                                                     language=en_language, text_labels_name=CMS_LABEL)}
    return layout.render(request, "education_group/tab_general_informations.html", context)


def _get_cms_label_data(cms_label, user_language):
    cms_label_data = OrderedDict()
    translated_labels = mdl_cms.translated_text_label.search(text_entity=entity_name.OFFER_YEAR,
                                                             labels=cms_label,
                                                             language=user_language)
    for label in cms_label:
        translated_text = next((trans.label for trans in translated_labels if trans.text_label.label == label), None)
        cms_label_data[label] = translated_text
    return cms_label_data


@login_required
@permission_required('base.can_access_offer', raise_exception=True)
def education_group_administrative_data(request, education_group_year_id):
    return _education_group_administrative_data_tab(request, education_group_year_id)


def _education_group_administrative_data_tab(request, education_group_year_id):
    education_group_year = mdl.education_group_year.find_by_id(education_group_year_id)
    context = {'education_group_year': education_group_year,
               'course_enrollment':get_dates(academic_calendar_type.COURSE_ENROLLMENT, education_group_year),
               'mandataries': mdl.mandatary.find_by_education_group_year(education_group_year),
               'pgm_mgrs': mdl.program_manager.find_by_education_group(education_group_year.education_group)}
    context.update({'exam_enrollments': get_sessions_dates(academic_calendar_type.EXAM_ENROLLMENTS,
                                                           education_group_year)})
    context.update({'scores_exam_submission': get_sessions_dates(academic_calendar_type.SCORES_EXAM_SUBMISSION,
                                                                 education_group_year)})
    context.update({'dissertation_submission': get_sessions_dates(academic_calendar_type.DISSERTATION_SUBMISSION,
                                                                  education_group_year)})
    context.update({'deliberation': get_sessions_dates(academic_calendar_type.DELIBERATION,
                                                       education_group_year)})
    context.update({'scores_exam_diffusion': get_sessions_dates(academic_calendar_type.SCORES_EXAM_DIFFUSION,
                                                                education_group_year)})
    return layout.render(request, "education_group/tab_administrative_data.html", context)


def get_sessions_dates(an_academic_calendar_type, an_education_group_year):
    date_dict = {}
    cpt = 1
    while cpt <= 3:
        session1 = mdl.session_exam_calendar.get_by_session_reference_and_academic_year(cpt,
                                                                                        an_academic_calendar_type,
                                                                                        an_education_group_year.academic_year)
        if session1:
            dates = mdl.offer_year_calendar.get_by_education_group_year_and_academic_calendar(session1.academic_calendar,
                                                                                              an_education_group_year)
            key = 'session{}'.format(cpt)
            date_dict.update({key: dates})
        cpt = cpt + 1
    return date_dict


def get_dates(an_academic_calendar_type, an_education_group_year):
    ac = mdl.academic_calendar.get_by_reference_and_academic_year(an_academic_calendar_type,
                                                                  an_education_group_year.academic_year)
    if ac:
        dates = mdl.offer_year_calendar.get_by_education_group_year_and_academic_calendar(ac, an_education_group_year)
        return {'dates': dates}
    else:
        return {}
