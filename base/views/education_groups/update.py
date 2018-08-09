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
from django import forms
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from waffle.decorators import waffle_flag

from base.forms.education_group.common import EducationGroupModelForm
from base.forms.education_group.group import GroupForm
from base.forms.education_group.mini_training import MiniTrainingForm
from base.forms.education_group.training import TrainingForm
from base.models.education_group_year import EducationGroupYear
from base.models.enums import education_group_categories
from base.views import layout
from base.views.common import display_success_messages
from base.views.education_groups.perms import can_change_education_group
from base.views.learning_units.perms import PermissionDecoratorWithUser


@login_required
@waffle_flag("education_group_update")
@PermissionDecoratorWithUser(can_change_education_group, "education_group_year_id", EducationGroupYear)
def update_education_group(request, root_id, education_group_year_id):
    education_group_year = get_object_or_404(EducationGroupYear, pk=education_group_year_id)
    root = get_object_or_404(EducationGroupYear, pk=root_id)

    view_function = _get_view(education_group_year.education_group_type.category)
    return view_function(request, education_group_year, root)


def _get_view(category):
    return {
        education_group_categories.TRAINING: _update_training,
        education_group_categories.MINI_TRAINING: _update_mini_training,
        education_group_categories.GROUP: _update_group
    }[category]


def _common_success_redirect(request, education_group_year, root):
    success_msg = _("{} successfully updated").format(_(education_group_year.education_group_type.category))
    display_success_messages(request, success_msg)
    url = reverse("education_group_read", args=[root.pk, education_group_year.id])
    return redirect(url)


def _update_group(request, education_group_year, root):
    # TODO :: IMPORTANT :: Fix urls patterns to get the GroupElementYear_id and the root_id in the url path !
    # TODO :: IMPORTANT :: Need to update form to filter on list of parents, not only on the first direct parent
    form_education_group_year = GroupForm(request.POST or None, instance=education_group_year)
    html_page = "education_group/update_groups.html"

    if form_education_group_year.is_valid():
        return _common_success_redirect(request, form_education_group_year.save(), root)

    return layout.render(request, html_page, {
        "education_group_year": education_group_year,
        "form_education_group_year": form_education_group_year.forms[forms.ModelForm],
        "form_education_group": form_education_group_year.forms[EducationGroupModelForm]
    })


def _update_training(request, education_group_year, root):
    # TODO :: IMPORTANT :: Fix urls patterns to get the GroupElementYear_id and the root_id in the url path !
    # TODO :: IMPORTANT :: Need to update form to filter on list of parents, not only on the first direct parent
    form_education_group_year = TrainingForm(request.POST or None, instance=education_group_year)
    if form_education_group_year.is_valid():
        return _common_success_redirect(request, form_education_group_year.save(), root)

    return layout.render(request, "education_group/update_trainings.html", {
        "education_group_year": education_group_year,
        "form_education_group_year": form_education_group_year.forms[forms.ModelForm],
        "form_education_group": form_education_group_year.forms[EducationGroupModelForm]
    })


def _update_mini_training(request, education_group_year, root):
    # TODO :: IMPORTANT :: Fix urls patterns to get the GroupElementYear_id and the root_id in the url path !
    # TODO :: IMPORTANT :: Need to upodate form to filter on list of parents, not only on the first direct parent
    form = MiniTrainingForm(request.POST or None, instance=education_group_year)

    if form.is_valid():
        return _common_success_redirect(request, form.save(), root)

    return layout.render(request, "education_group/update_minitrainings.html", {
        "form_education_group_year": form.forms[forms.ModelForm],
        "education_group_year": education_group_year,
        "form_education_group": form.forms[EducationGroupModelForm]
    })
