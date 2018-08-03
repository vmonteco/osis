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
from collections.__init__ import OrderedDict
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic import DetailView

from base import models as mdl
from base.business.education_group import assert_category_of_education_group_year, can_user_edit_administrative_data
from base.business.education_groups import perms
from base.forms.education_group_general_informations import EducationGroupGeneralInformationsForm
from base.models.education_group_year import EducationGroupYear
from base.models.enums import education_group_categories, academic_calendar_type
from base.models.person import Person
from cms import models as mdl_cms
from cms.enums import entity_name

CODE_SCS = 'code_scs'
TITLE = 'title'
CREDITS_MIN = "credits_min"
CREDITS_MAX = "credits_max"
BLOCK = "block"
QUADRIMESTER_DEROGATION = "quadrimester_derogation"
LINK_TYPE = "link_type"
NUMBER_SESSIONS = 3


@method_decorator(login_required, name='dispatch')
class EducationGroupGenericDetailView(PermissionRequiredMixin, DetailView):
    # DetailView
    model = EducationGroupYear
    context_object_name = "education_group_year"
    pk_url_kwarg = 'education_group_year_id'

    # PermissionRequiredMixin
    permission_required = 'base.can_access_education_group'
    raise_exception = True

    limited_by_category = None

    def get_person(self):
        return get_object_or_404(Person, user=self.request.user)

    def get_root(self):
        return get_object_or_404(EducationGroupYear, pk=self.kwargs.get("root_id"))

    def get_group_to_parent(self):
        return self.request.GET.get("group_to_parent")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # This objects are mandatory for all education group views
        context['person'] = self.get_person()

        # TODO same param
        context['root'] = self.get_root()
        context['root_id'] = self.kwargs.get("root_id")
        context['parent'] = self.get_root()

        context["education_group_year"] = self.get_object()
        context['group_to_parent'] = self.get_group_to_parent()
        context['can_change_education_group'] = perms.is_eligible_to_change_education_group(
            person=self.get_person(),
            education_group=context['object'],
        )
        return context

    def get(self, request, *args, **kwargs):
        if self.limited_by_category:
            assert_category_of_education_group_year(self.get_object(), self.limited_by_category)
        return super().get(request, *args, **kwargs)


class EducationGroupRead(EducationGroupGenericDetailView):
    templates = {
        education_group_categories.TRAINING: "education_group/identification_training_details.html",
        education_group_categories.MINI_TRAINING: "education_group/identification_mini_training_details.html",
        education_group_categories.GROUP: "education_group/identification_group_details.html"
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # TODO Use value_list
        context["education_group_languages"] = [
            education_group_language.language.name for education_group_language in
            mdl.education_group_language.find_by_education_group_year(self.object)
        ]
        context['enums'] = mdl.enums.education_group_categories

        return context

    def get_template_names(self):
        return self.templates.get(self.object.education_group_type.category)


class EducationGroupDiplomas(EducationGroupGenericDetailView):
    template_name = "education_group/tab_diplomas.html"
    limited_by_category = (education_group_categories.TRAINING,)


class EducationGroupGeneralInformation(EducationGroupGenericDetailView):
    template_name = "education_group/tab_general_informations.html"
    limited_by_category = (education_group_categories.TRAINING, education_group_categories.MINI_TRAINING)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        cms_label = mdl_cms.translated_text.find_labels_list_by_label_entity_and_reference(
            entity_name.OFFER_YEAR, self.object.pk)

        fr_language = next((lang for lang in settings.LANGUAGES if lang[0] == 'fr-be'), None)
        en_language = next((lang for lang in settings.LANGUAGES if lang[0] == 'en'), None)

        context.update({
            'can_edit_information': self.request.user.has_perm('base.can_edit_educationgroup_pedagogy'),
            'cms_labels_translated': _get_cms_label_data(
                cms_label, mdl.person.get_user_interface_language(self.request.user)),
            'form_french': EducationGroupGeneralInformationsForm(
                education_group_year=self.object,
                language=fr_language,
                text_labels_name=cms_label
            ),
            'form_english': EducationGroupGeneralInformationsForm(
                education_group_year=self.object,
                language=en_language,
                text_labels_name=cms_label
            )
        })

        return context


def _get_cms_label_data(cms_label, user_language):
    cms_label_data = OrderedDict()
    translated_labels = mdl_cms.translated_text_label.search(
        text_entity=entity_name.OFFER_YEAR,
        labels=cms_label,
        language=user_language
    )

    for label in cms_label:
        translated_text = next((trans.label for trans in translated_labels if trans.text_label.label == label), None)
        cms_label_data[label] = translated_text

    return cms_label_data


class EducationGroupAdministrativeData(EducationGroupGenericDetailView):
    template_name = "education_group/tab_administrative_data.html"
    limited_by_category = (education_group_categories.TRAINING,)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'course_enrollment': get_dates(academic_calendar_type.COURSE_ENROLLMENT, self.object),
            'mandataries': mdl.mandatary.find_by_education_group_year(self.object),
            'pgm_mgrs': mdl.program_manager.find_by_education_group(self.object.education_group),
            'exam_enrollments': get_sessions_dates(academic_calendar_type.EXAM_ENROLLMENTS, self.object),
            'scores_exam_submission': get_sessions_dates(academic_calendar_type.SCORES_EXAM_SUBMISSION, self.object),
            'dissertation_submission': get_sessions_dates(academic_calendar_type.DISSERTATION_SUBMISSION, self.object),
            'deliberation': get_sessions_dates(academic_calendar_type.DELIBERATION, self.object),
            'scores_exam_diffusion': get_sessions_dates(academic_calendar_type.SCORES_EXAM_DIFFUSION, self.object),
            "can_edit_administrative_data": can_user_edit_administrative_data(self.request.user, self.object)
        })

        return context


def get_sessions_dates(an_academic_calendar_type, an_education_group_year):
    date_dict = {}

    for session_number in range(NUMBER_SESSIONS):
        session = mdl.session_exam_calendar.get_by_session_reference_and_academic_year(
            session_number + 1,
            an_academic_calendar_type,
            an_education_group_year.academic_year)
        if session:
            dates = mdl.offer_year_calendar.get_by_education_group_year_and_academic_calendar(session.academic_calendar,
                                                                                              an_education_group_year)
            date_dict['session{}'.format(session_number + 1)] = dates

    return date_dict


def get_dates(an_academic_calendar_type, an_education_group_year):
    ac = mdl.academic_calendar.get_by_reference_and_academic_year(an_academic_calendar_type,
                                                                  an_education_group_year.academic_year)
    if ac:
        dates = mdl.offer_year_calendar.get_by_education_group_year_and_academic_calendar(ac, an_education_group_year)
        return {'dates': dates}
    else:
        return {}


class EducationGroupContent(EducationGroupGenericDetailView):
    template_name = "education_group/tab_content.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["group_elements"] = _group_elements(self.object)

        return context


def _group_elements(education_group_yr):
    group_elements = mdl.group_element_year.find_by_parent(education_group_yr)
    if group_elements.exists():
        return _get_group_elements_data(group_elements)

    return None


def _get_education_group_detail(dict_param, group_element):
    dict_param.update({CODE_SCS: group_element.child_branch.partial_acronym,
                       TITLE: group_element.child_branch.title,
                       CREDITS_MIN: group_element.min_credits,
                       CREDITS_MAX: group_element.max_credits,
                       BLOCK: None,
                       QUADRIMESTER_DEROGATION: group_element.quadrimester_derogation,
                       LINK_TYPE: group_element.link_type
                       })
    return dict_param


def _get_learning_unit_detail(dict_param, group_element):
    dict_param.update({CODE_SCS: group_element.child_leaf.acronym,
                       TITLE: group_element.child_leaf.specific_title,
                       CREDITS_MIN: None,
                       CREDITS_MAX: None,
                       BLOCK: group_element.block,
                       QUADRIMESTER_DEROGATION: group_element.quadrimester_derogation,
                       LINK_TYPE: group_element.link_type})
    return dict_param


# @TODO: Enhance research via queryset annotate
def _get_group_elements_data(group_elements):
    group_elements_data = []
    for group_element in group_elements:
        group_element_values = {'group_element': group_element}
        if group_element.child_leaf:
            _get_learning_unit_detail(group_element_values, group_element)
        elif group_element.child_branch:
            _get_education_group_detail(group_element_values, group_element)
        group_elements_data.append(group_element_values)
    return _sorting(group_elements_data)


def _sorting(group_elements_data):
    return sorted(group_elements_data, key=lambda k: k.get('group_element').order)
