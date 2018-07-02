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
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import ugettext_lazy as _

from base.forms.education_group.create import CreateEducationGroupYearForm
from base.forms.education_group.edition import EducationGroupForm
from base.models.education_group_year import EducationGroupYear
from base.models.enums import education_group_categories
from base.views import layout
from base.views.common import display_success_messages, reverse_url_with_root
from base.views.education_groups.perms import can_change_education_group


@login_required
@user_passes_test(can_change_education_group)
def update_education_group(request, education_group_year_id):
    education_group_year = get_object_or_404(EducationGroupYear, pk=education_group_year_id)

    form_education_group = EducationGroupForm(request.POST or None, instance=education_group_year.education_group)
    form_education_group_year = CreateEducationGroupYearForm(request.POST or None, instance=education_group_year)

    if education_group_year.education_group_type.category != education_group_categories.GROUP:
        html_page = "education_group/identification_training_edit.html"
    else:
        html_page = "education_group/update.html"

    if form_education_group.is_valid() and form_education_group_year.is_valid():
        display_success_messages(request, _("Education group successfully updated"))
        url = reverse_url_with_root(request, "education_group_read", args=[education_group_year.id])
        return redirect(url)

    return layout.render(request, html_page, {
        "form_education_group_year": form_education_group_year,
        "education_group_year": education_group_year,
        "form_education_group": form_education_group
    })
