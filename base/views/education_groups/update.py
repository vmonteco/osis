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
from base.models.enums import education_group_categories
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import ugettext_lazy as _
from waffle.decorators import waffle_flag

from base.forms.education_group.create import GroupModelForm, EducationGroupModelForm, GroupForm
from base.forms.education_group.mini_training import MiniTrainingModelForm, MiniTrainingForm
from base.forms.education_group.training import TrainingEducationGroupYearForm, TrainingForm
from base.models.education_group_year import EducationGroupYear
from base.models.enums import education_group_categories
from base.views import layout
from base.views.common import display_success_messages, reverse_url_with_root
from base.views.education_groups.perms import can_change_education_group

from django import forms


@login_required
@waffle_flag("education_group_update")
@user_passes_test(can_change_education_group)
def update_education_group(request, education_group_year_id):
    education_group_year = get_object_or_404(EducationGroupYear, pk=education_group_year_id)

    view_function = _get_view(education_group_year.education_group_type.category)
    return view_function(request, education_group_year)


def _update_group(request, education_group_year):
    # form_education_group = EducationGroupForm(request.POST or None, instance=education_group_year.education_group)

    # if education_group_year.education_group_type.category != education_group_categories.GROUP:
    #     form_education_group_year = TrainingEducationGroupYearForm(request.POST or None, instance=education_group_year)
    #     html_page = "education_group/update_trainings.html"
    # else:
    form_education_group_year = GroupForm(request.POST or None, instance=education_group_year)
    html_page = "education_group/update_groups.html"

    if form_education_group_year.is_valid():
        display_success_messages(request, _("Education group successfully updated"))
        url = reverse_url_with_root(request, "education_group_read", args=[education_group_year.id])
        # form_education_group.save()
        form_education_group_year.save()
        return redirect(url)

    return layout.render(request, html_page, {
        "education_group_year": education_group_year,
        "form_education_group_year": form_education_group_year.forms[forms.ModelForm],
        # "form_education_group": form_education_group
    })


def _common_redirect_url(request, education_group_year):
    display_success_messages(request, _("Mini training successfully updated"))
    url = reverse_url_with_root(request, "education_group_read", args=[education_group_year.id])
    return redirect(url)

# def _get_template(education_group_year):
#     category = education_group_year.education_group_type.category
#     return {
#         education_group_categories.TRAINING: None, # to implement
#         education_group_categories.MINI_TRAINING: "education_group/minitraining_form.html",
#         education_group_categories.GROUP: "education_group/update.html"
#     }[category]


# TODO :: IMPORTANT :: Fix urls patterns to get the GroupElementYear_id and the root_id in the url path !
def _get_view(category):
    return {
        # TODO :: merge with TrainingForm
        education_group_categories.TRAINING: _update_training,
        # TODO :: pass parent in parameter (thanks to urls
        education_group_categories.MINI_TRAINING: _update_mini_training,
        # TODO :: pass parent in parameter
        education_group_categories.GROUP: _update_group
    }[category]


def _update_training(request, education_group_year):
    # form_education_group = EducationGroupForm(request.POST or None, instance=education_group_year.education_group)

    # if education_group_year.education_group_type.category != education_group_categories.GROUP:
    form_education_group_year = TrainingForm(request.POST or None, instance=education_group_year)
        # html_page = "education_group/update_trainings.html"
    # else:
    # form_education_group_year = CreateEducationGroupYearForm(request.POST or None, instance=education_group_year)
    # html_page = "education_group/update_groups.html"

    if form_education_group_year.is_valid():
        display_success_messages(request, _("Education group successfully updated"))
        url = reverse_url_with_root(request, "education_group_read", args=[education_group_year.id])
        # form_education_group.save()
        form_education_group_year.save()
        return redirect(url)

    return layout.render(request, "education_group/update_trainings.html", {
        "education_group_year": education_group_year,
        "form_education_group_year": form_education_group_year.forms[forms.ModelForm],
        "form_education_group": form_education_group_year.forms[EducationGroupModelForm]
    })

#
# # TODO :: IMPORTANT :: Fix urls patterns to get the GroupElementYear_id and the root_id in the url path !
# def _instanciate_form_from_category(request, education_group_year):
#     category = education_group_year.education_group_type.category
#     return {
#         # TODO :: merge with TrainingForm
#         education_group_categories.TRAINING: None, # to implement
#         # TODO :: pass parent in parameter (thanks to urls
#         education_group_categories.MINI_TRAINING: MiniFormationForm(request.POST or None, instance=education_group_year),
#         # TODO :: pass parent in parameter
#         education_group_categories.GROUP: CreateEducationGroupYearForm(request.POST or None, instance=education_group_year)
#     }[category]


def _update_mini_training(request, education_group_year):

    form = MiniTrainingForm(request.POST or None, instance=education_group_year)
    print(str(request.POST))

    if form.is_valid():
        education_group_year = form.save()

        display_success_messages(request, _("Mini training successfully updated"))

        url = reverse_url_with_root(request, "education_group_read", args=[education_group_year.id])

        return redirect(url)

    return layout.render(request, "education_group/minitraining_form.html", {
        "form_education_group_year": form.forms[forms.ModelForm],
        "education_group_year": education_group_year,
        "form_education_group": form.forms[EducationGroupModelForm]
    })

