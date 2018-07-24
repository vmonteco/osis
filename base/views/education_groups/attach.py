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

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls import reverse
from waffle.decorators import waffle_flag

from base.models import group_element_year
from base.models.education_group_year import EducationGroupYear
from base.utils.cache import cache_filter, cache
from base.views.education_groups.perms import can_change_education_group
from base.views.learning_units.perms import PermissionDecoratorWithUser


@login_required
@waffle_flag("education_group_attach")
@PermissionDecoratorWithUser(can_change_education_group, "education_group_year_id", EducationGroupYear)
@cache_filter()
def education_group_attach(request, education_group_year_id):
    parent_id = int(request.GET.get('education_group_year_id'))
    child_id = int(cache.get('education_group_year_id'))
    group_element_year.get_or_create_group_element_year(
        parent=EducationGroupYear.objects.get(id=parent_id),
        child=EducationGroupYear.objects.get(id=child_id)
    )
    cache.set('education_group_year_id', None, timeout=None)
    return redirect(reverse('education_group_read', kwargs={'education_group_year_id': education_group_year_id}))
