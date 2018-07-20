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
from base.models.group_element_year import GroupElementYear
from base.utils.cache import cache_filter
from base.views.education_groups.perms import can_change_education_group

from waffle.decorators import waffle_flag


@login_required
@waffle_flag("education_group_attach")
@user_passes_test(can_change_education_group)
@cache_filter()
def education_group_attach(request, parent_id):
    group_to_attach = GroupElementYear.objects.get_or_create(
        parent=parent_id,
        child_branch=request.GET.get("education_group_year_id")
    )
    return group_to_attach
