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

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from waffle.decorators import waffle_flag

from base.utils.cache import cache


@login_required
@waffle_flag("education_group_select")
def education_group_select(request, root_id=None, education_group_year_id=None):
    child_to_cache_id = request.GET.get('child_to_cache_id')
    cache.set('child_to_cache_id', child_to_cache_id, timeout=None)
    if request.is_ajax():
        return HttpResponse(HTTPStatus.OK)
    else:
        return redirect(reverse(
            'education_group_read',
            args=[
                root_id,
                education_group_year_id,
            ]
        ))
