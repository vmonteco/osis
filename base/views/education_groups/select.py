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
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from waffle.decorators import waffle_flag

from base.business import group_element_years
from base.business.group_element_years.management import LEARNING_UNIT_YEAR
from base.models.education_group_year import EducationGroupYear
from base.models.learning_unit_year import LearningUnitYear


@login_required
@waffle_flag("education_group_select")
def education_group_select(request, root_id=None, education_group_year_id=None):
    education_group_year = get_object_or_404(EducationGroupYear, pk=request.POST['child_to_cache_id'])
    group_element_years.management.select_education_group_year(education_group_year)
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


@login_required
@waffle_flag("education_group_select")
@require_http_methods(['POST'])
def learning_unit_select(request, learning_unit_year_id):
    learning_unit_year = get_object_or_404(LearningUnitYear, pk=learning_unit_year_id)
    group_element_years.management.select_learning_unit_year(learning_unit_year)
    if request.is_ajax():
        return HttpResponse(HTTPStatus.OK)
    else:
        return redirect(reverse(
            'learning_unit',
            args=[learning_unit_year_id]
        ))
