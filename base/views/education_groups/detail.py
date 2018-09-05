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
import json
from collections import OrderedDict

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import F, Case, When, OuterRef, Exists
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import DetailView

from base import models as mdl
from base.business.education_group import assert_category_of_education_group_year, can_user_edit_administrative_data
from base.business.education_groups import perms
from base.business.group_element_years.management import EDUCATION_GROUP_YEAR, LEARNING_UNIT_YEAR
from base.forms.education_group_general_informations import EducationGroupGeneralInformationsForm
from base.models.education_group_year import EducationGroupYear
from base.models.enums import education_group_categories, academic_calendar_type
from base.models.person import Person
from base.models.prerequisite import Prerequisite
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # This objects are mandatory for all education group views
        context['person'] = self.get_person()

        root = self.get_root()
        # TODO same param
        context['root'] = root
        context['root_id'] = root.pk
        context['parent'] = root
        context['tree'] = json.dumps(NodeBranchJsTree(root).to_json())

        context['group_to_parent'] = self.request.GET.get("group_to_parent") or '0'
        context['can_change_education_group'] = perms.is_eligible_to_change_education_group(
            person=self.get_person(),
            education_group=context['object'],
        )
        context['enums'] = mdl.enums.education_group_categories

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

        context["group_element_years"] = self.object.groupelementyear_set.annotate(
                code_scs=Case(
                        When(child_leaf__isnull=False, then=F("child_leaf__acronym")),
                        When(child_branch__isnull=False, then=F("child_branch__acronym")),
                     ),
                title=Case(
                        When(child_leaf__isnull=False, then=F("child_leaf__specific_title")),
                        When(child_branch__isnull=False, then=F("child_branch__title")),
                     ),
            ).order_by('order')

        return context


class EducationGroupUsing(EducationGroupGenericDetailView):
    template_name = "education_group/tab_utilization.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["group_element_years"] = mdl.group_element_year.find_by_child_branch(self.object) \
            .select_related("parent")
        return context


class NodeBranchJsTree:
    """ Use to generate json from a list of education group years compatible with jstree """
    element_type = EDUCATION_GROUP_YEAR

    def __init__(self, root, group_element_year=None):
        self.root = root
        self.group_element_year = group_element_year
        self.children = self.generate_children()

    def generate_children(self):
        result = []
        has_prerequisite = Prerequisite.objects.filter(
            education_group_year__id=self.root.id,
            learning_unit_year__id=OuterRef("child_leaf__id"),
        ).exclude(prerequisite__exact='')

        for group_element_year in self.education_group_year.groupelementyear_set.all()\
                .annotate(has_prerequisites=Exists(has_prerequisite)):
            if group_element_year.child_branch:
                result.append(NodeBranchJsTree(self.root, group_element_year))
            else:
                result.append(NodeLeafJsTree(self.root, group_element_year))

        return result

    def to_json(self):
        return {
            'text': self.education_group_year.verbose,
            'children': [child.to_json() for child in self.children],
            'a_attr': {
                'href': self.get_url(),
                'root': self.root.pk,
                'group_element_year': self.group_element_year and self.group_element_year.pk,
                'education_group_year': self.education_group_year.pk,
                'element_type': self.element_type
            }
        }

    @property
    def education_group_year(self):
        return self.root if not self.group_element_year else self.group_element_year.child_branch

    def get_url(self):
        group_to_parent = self.group_element_year.pk if self.group_element_year else 0
        url = reverse('education_group_read', args=[self.root.pk, self.education_group_year.pk])

        return url + "?group_to_parent=" + str(group_to_parent)


class NodeLeafJsTree(NodeBranchJsTree):
    """ The leaf has no child """
    element_type = LEARNING_UNIT_YEAR

    @property
    def learning_unit_year(self):
        if self.group_element_year:
            return self.group_element_year.child_leaf

    @property
    def education_group_year(self):
        return

    def to_json(self):
        return {
            'text': self.learning_unit_year.acronym,
            'icon': "glyphicon glyphicon-leaf" if self.group_element_year.has_prerequisites else "jstree-file",
            'a_attr': {
                'href': self.get_url(),
                'root': self.root.pk,
                'group_element_year': self.group_element_year and self.group_element_year.pk,
                'learning_unit_year': self.learning_unit_year.pk,
                'element_type': self.element_type
            }
        }

    def get_url(self):
        group_to_parent = self.group_element_year.pk if self.group_element_year else 0
        url = reverse('learning_unit_utilization', args=[self.root.pk, self.learning_unit_year.pk])

        return url + "?group_to_parent=" + str(group_to_parent)

    def generate_children(self):
        return []
