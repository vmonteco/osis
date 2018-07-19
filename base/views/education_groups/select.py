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
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.status import HTTP_200_OK

from base.models.education_group_year import EducationGroupYear
from base.utils.cache import cache_filter
from base.views.education_groups.perms import can_change_education_group

from waffle.decorators import waffle_flag

from base.views.education_groups.update import _get_view


@login_required
@waffle_flag("education_group_select")
@user_passes_test(can_change_education_group)
@cache_filter()
def education_group_select(request, education_group_year_id=None):
    if request.is_ajax():
        return JsonResponse({'status': HTTP_200_OK})
    else:
        education_group_year = get_object_or_404(EducationGroupYear, pk=education_group_year_id)
        view_function = _get_view(education_group_year.education_group_type.category)
        return view_function(request, education_group_year)
