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
from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404

from base.models.learning_achievements import LearningAchievements, find_learning_unit_achievement
from django.views.decorators.http import require_http_methods

EN_CODE_LANGAGUE = 'EN'


def operation(learning_achievement_id, operation_string):
    achievement_fr = get_object_or_404(LearningAchievements, pk=learning_achievement_id)
    lu_yr_id = achievement_fr.learning_unit_year.id
    if achievement_fr:
        achievement_en = find_learning_unit_achievement(achievement_fr.learning_unit_year,
                                                        EN_CODE_LANGAGUE,
                                                        achievement_fr.order)
        func = getattr(achievement_fr, operation_string)
        func()
        if achievement_en:
            func = getattr(achievement_en, operation_string)
            func()
    return HttpResponseRedirect(reverse("learning_unit_specifications",
                                        kwargs={'learning_unit_year_id': lu_yr_id}))


@login_required
@permission_required('base.can_access_learningunit', raise_exception=True)
@require_http_methods(['POST'])
def management(request):
    return operation(request.POST.get('achievement_id'), request.POST.get('action'))
