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

from base.models.learning_achievements import LearningAchievements, search

EN_CODE_LANGAGUE = 'EN'


@login_required
@permission_required('base.can_access_learningunit', raise_exception=True)
def delete(request, learning_achievement_id):
    a_learning_achievement_fr = get_object_or_404(LearningAchievements, pk=learning_achievement_id)
    lu_yr_id = a_learning_achievement_fr.learning_unit_year.id
    if a_learning_achievement_fr:
        a_learning_achievement_en = get_en_learning_achievement(a_learning_achievement_fr)
        a_learning_achievement_fr.delete()
        if a_learning_achievement_en:
            a_learning_achievement_en.first().delete()

    return HttpResponseRedirect(reverse("learning_unit_specifications",
                                        kwargs={'learning_unit_year_id': lu_yr_id}))


@login_required
@permission_required('base.can_access_learningunit', raise_exception=True)
def up(request, learning_achievement_id):
    a_learning_achievement_fr = get_object_or_404(LearningAchievements, pk=learning_achievement_id)
    lu_yr_id = a_learning_achievement_fr.learning_unit_year.id
    if a_learning_achievement_fr:
        a_learning_achievement_en = get_en_learning_achievement(a_learning_achievement_fr)
        a_learning_achievement_fr.up()
        if a_learning_achievement_en:
            a_learning_achievement_en.first().up()

    return HttpResponseRedirect(reverse("learning_unit_specifications",
                                        kwargs={'learning_unit_year_id': lu_yr_id}))


@login_required
@permission_required('base.can_access_learningunit', raise_exception=True)
def down(request, learning_achievement_id):
    a_learning_achievement_fr = get_object_or_404(LearningAchievements, pk=learning_achievement_id)
    lu_yr_id = a_learning_achievement_fr.learning_unit_year.id
    if a_learning_achievement_fr:
        a_learning_achievement_en = get_en_learning_achievement(a_learning_achievement_fr)
        a_learning_achievement_fr.down()
        if a_learning_achievement_en:
            a_learning_achievement_en.first().down()

    return HttpResponseRedirect(reverse("learning_unit_specifications",
                                        kwargs={'learning_unit_year_id': lu_yr_id}))


def get_en_learning_achievement(a_learning_achievement_fr):
    a_learning_achievement_en = search(a_learning_achievement_fr.learning_unit_year,
                                       EN_CODE_LANGAGUE,
                                       a_learning_achievement_fr.order)
    return a_learning_achievement_en
