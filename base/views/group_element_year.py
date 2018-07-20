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
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import ViewDoesNotExist
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.utils.translation import ugettext_lazy as _
from waffle.decorators import waffle_flag

from base import models as mdl
from base.views.common import display_success_messages
from base.views.education_groups import perms
from osis_common.document.pdf_build import Render


@login_required
@waffle_flag("education_group_update")
@user_passes_test(perms.can_change_education_group)
def management(request, root_id, education_group_year_id, group_element_year_id):
    group_element_year = get_object_or_404(mdl.group_element_year.GroupElementYear, pk=group_element_year_id)
    action_method = _get_action_method(request)
    response = action_method(request, group_element_year)
    if response:
        return response
    # @Todo: Correct with new URL
    success_url = reverse('education_group_content',
                          kwargs={'education_group_year_id': education_group_year_id}) + '?root={}'.format(root_id)
    return redirect(success_url)


@require_http_methods(['POST'])
def _up(request, group_element_year):
    success_msg = _("The %(acronym)s has been moved") % {'acronym': group_element_year.child}
    group_element_year.up()
    display_success_messages(request, success_msg)


@require_http_methods(['POST'])
def _down(request, group_element_year):
    success_msg = _("The %(acronym)s has been moved") % {'acronym': group_element_year.child}
    group_element_year.down()
    display_success_messages(request, success_msg)


@require_http_methods(['POST'])
def _detatch(request, group_element_year):
    success_msg = _("The %(acronym)s has been detatched") % {'acronym': group_element_year.child}
    group_element_year.delete()
    display_success_messages(request, success_msg)


@require_http_methods(['GET', 'POST'])
def _edit(request, group_element_year):
    raise ViewDoesNotExist


def _get_action_method(request):
    AVAILABLE_ACTIONS = {
        'up': _up,
        'down': _down,
        'detatch': _detatch,
        'edit': _edit
    }
    data = getattr(request, request.method, {})
    action = data.get('action')
    if action not in AVAILABLE_ACTIONS.keys():
        raise AttributeError('Action should be {}'.format(','.join(AVAILABLE_ACTIONS.keys())))
    return AVAILABLE_ACTIONS[action]


@login_required
def pdf_content(request, education_group_year_id):
    education_group_year = mdl.education_group_year.find_by_id(education_group_year_id)

    #group_element_years = education_group_year.parents.all()
    #children = [group_element_year for group_element_year in group_element_years]
    #context = {education_group_year: children}

    parent = education_group_year


    return Render.render('education_group/pdf.html', {'parent': parent})
