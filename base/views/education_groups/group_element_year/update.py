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
import abc

from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, NoReverseMatch
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_http_methods
from django.views.generic import DeleteView
from django.views.generic import UpdateView
from waffle.decorators import waffle_flag

from base.business import group_element_years
from base.business.group_element_years.management import SELECT_CACHE_KEY, select_education_group_year, \
    LEARNING_UNIT_YEAR, EDUCATION_GROUP_YEAR
from base.forms.education_group.group_element_year import UpdateGroupElementYearForm
from base.models.education_group_year import EducationGroupYear
from base.models.exceptions import IncompatiblesTypesException
from base.models.group_element_year import GroupElementYear, get_group_element_year_by_id
from base.models.learning_unit_year import LearningUnitYear
from base.views.common import display_success_messages, display_warning_messages
from base.views.common_classes import AjaxTemplateMixin, FlagMixin, RulesRequiredMixin
from base.views.education_groups import perms
from base.views.education_groups.select import build_success_message, build_success_json_response, \
    learning_unit_select


@login_required
@waffle_flag("education_group_update")
def management(request, root_id, education_group_year_id, group_element_year_id):
    group_element_year_id = int(group_element_year_id)
    group_element_year = get_group_element_year_by_id(group_element_year_id) if group_element_year_id else None
    action_method = _get_action_method(request)
    perms.can_change_education_group(request.user, group_element_year.parent)
    source = _get_data(request, 'source')
    response = action_method(
        request,
        group_element_year,
        root_id=root_id,
        education_group_year_id=education_group_year_id,
        source=source,
    )
    if response:
        return response

    return redirect(request.META.get('HTTP_REFERER'))


def _get_data(request, name):
    return getattr(request, request.method, {}).get(name)


@login_required
@waffle_flag("education_group_update")
def proxy_management(request):
    root_id = _get_data(request, 'root_id')
    group_element_year_id = _get_data(request, 'group_element_year_id')
    if _get_data(request, 'action') == "select":
        element_type = _get_data(request, 'element_type')
        element_id = _get_data(request, 'element_id')
        return _select(request, element_type, element_id)
    else:
        education_group_year_id = _get_data(request, 'education_group_year_id')
        return management(
            request,
            root_id=root_id,
            education_group_year_id=education_group_year_id,
            group_element_year_id=group_element_year_id,
        )


@require_http_methods(['POST'])
def _up(request, group_element_year, *args, **kwargs):
    success_msg = _("The %(acronym)s has been moved") % {'acronym': group_element_year.child}
    group_element_year.up()
    display_success_messages(request, success_msg)


@require_http_methods(['POST'])
def _down(request, group_element_year, *args, **kwargs):
    success_msg = _("The %(acronym)s has been moved") % {'acronym': group_element_year.child}
    group_element_year.down()
    display_success_messages(request, success_msg)


@require_http_methods(['GET', 'POST'])
def _detach(request, group_element_year, *args, **kwargs):
    return DetachGroupElementYearView.as_view()(
        request,
        group_element_year_id=group_element_year.pk,
        *args,
        **kwargs
    )


@require_http_methods(['GET', 'POST'])
def _attach(request, group_element_year, *args, **kwargs):
    parent = get_object_or_404(EducationGroupYear, pk=kwargs['education_group_year_id'])
    try:
        group_element_years.management.attach_from_cache(parent)
        success_msg = _("Attached to \"%(acronym)s\"") % {'acronym': parent}
        display_success_messages(request, success_msg)
    except ObjectDoesNotExist:
        warning_msg = _("Please Select or Move an item before Attach it")
        display_warning_messages(request, warning_msg)
    except IncompatiblesTypesException as e:
        warning_msg = e.errors
        display_warning_messages(request, warning_msg)
    except IntegrityError as e:
        warning_msg = _(str(e))
        display_warning_messages(request, warning_msg)


@require_http_methods(['POST'])
def _select(request, element_type, element_id):
    if element_type == LEARNING_UNIT_YEAR:
        learning_unit_year = get_object_or_404(LearningUnitYear, pk=element_id)
        learning_unit_select(request, learning_unit_year.id)
        success_msg = build_success_message(learning_unit_year)
    elif element_type == EDUCATION_GROUP_YEAR:
        education_group_year = get_object_or_404(EducationGroupYear, pk=element_id)
        select_education_group_year(education_group_year)
        success_msg = build_success_message(education_group_year)
    return build_success_json_response(success_msg)


def _get_action_method(request):
    AVAILABLE_ACTIONS = {
        'up': _up,
        'down': _down,
        'detach': _detach,
        'attach': _attach,
    }
    data = getattr(request, request.method, {})
    action = data.get('action')
    if action not in AVAILABLE_ACTIONS.keys():
        raise AttributeError('Action should be {}'.format(','.join(AVAILABLE_ACTIONS.keys())))
    return AVAILABLE_ACTIONS[action]


@method_decorator(login_required, name='dispatch')
class GenericUpdateGroupElementYearMixin(FlagMixin, RulesRequiredMixin, SuccessMessageMixin, AjaxTemplateMixin):
    model = GroupElementYear
    context_object_name = "group_element_year"
    pk_url_kwarg = "group_element_year_id"

    # FlagMixin
    flag = "education_group_update"

    # RulesRequiredMixin
    raise_exception = True
    rules = [perms.can_change_education_group]

    @abc.abstractmethod
    def _call_rule(self, rule):
        return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['root'] = self.kwargs["root_id"]
        return context

    def get_root(self):
        return get_object_or_404(EducationGroupYear, pk=self.kwargs.get("root_id"))


class UpdateGroupElementYearView(GenericUpdateGroupElementYearMixin, UpdateView):
    # UpdateView
    form_class = UpdateGroupElementYearForm
    template_name = "education_group/group_element_year_comment.html"

    def _call_rule(self, rule):
        """ The permission is computed from the education_group_year """
        return rule(self.request.user, self.education_group_year)

    # SuccessMessageMixin
    def get_success_message(self, cleaned_data):
        return _("The comments of %(acronym)s has been updated") % {'acronym': self.object.child}

    def get_success_url(self):
        return reverse("education_group_content", args=[self.kwargs["root_id"], self.education_group_year.pk])

    @property
    def education_group_year(self):
        return get_object_or_404(EducationGroupYear, pk=self.kwargs.get("education_group_year_id"))


class DetachGroupElementYearView(GenericUpdateGroupElementYearMixin, DeleteView):
    # DeleteView
    template_name = "education_group/group_element_year/confirm_detach.html"

    def delete(self, request, *args, **kwargs):
        success_msg = _("\"%(child)s\" has been detached from \"%(parent)s\"") % {
            'child': self.get_object().child,
            'parent': self.get_object().parent,
        }
        display_success_messages(request, success_msg)
        return super().delete(request, *args, **kwargs)

    def _call_rule(self, rule):
        """ The permission is computed from the education_group_year """
        return rule(self.request.user, self.group_element_year.parent)

    def get_success_url(self):
        try:
            return reverse(self.kwargs.get('source'), args=[self.kwargs["root_id"], self.kwargs["root_id"]])
        except NoReverseMatch:
            return reverse("education_group_read", args=[self.kwargs["root_id"], self.kwargs["root_id"]])

    @property
    def group_element_year(self):
        return get_object_or_404(GroupElementYear, pk=self.kwargs.get("group_element_year_id"))
