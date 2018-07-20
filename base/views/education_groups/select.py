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
from http import HTTPStatus

from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse

from base.utils.cache import cache_filter, cache
from base.views.education_groups.perms import can_change_education_group

from waffle.decorators import waffle_flag


@login_required
@waffle_flag("education_group_select")
@user_passes_test(can_change_education_group)
@cache_filter()
def education_group_select(request, education_group_year_id=None):
    cache.set('education_group_year_id', education_group_year_id, timeout=None)
    if request.is_ajax():
        return HttpResponse(HTTPStatus.OK)
    else:
        return redirect(reverse('education_group_read', kwargs={'education_group_year_id': education_group_year_id}))
