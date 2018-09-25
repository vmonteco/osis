############################################################################
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
############################################################################
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic.detail import SingleObjectMixin

from base.models.education_group_achievement import EducationGroupAchievement
from base.models.education_group_detailed_achievement import EducationGroupDetailedAchievement
from base.models.education_group_year import EducationGroupYear


class EducationGroupAchievementMixin(SingleObjectMixin):
    model = EducationGroupAchievement
    context_object_name = "education_group_achievement"
    pk_url_kwarg = 'education_group_achievement_pk'

    def get_success_url(self):
        # Redirect to a page fragment
        url = reverse(
            "education_group_skills_achievements",
            args=[
                self.kwargs['root_id'],
                self.kwargs['education_group_year_id'],
            ]
        )

        if hasattr(self, "object"):
            # Remove the last / otherwise URL will be malformed
            url = url.rstrip('/') + "#{}_{}".format(self.context_object_name, self.object.pk)

        return url

    def get_education_group_year(self):
        return get_object_or_404(EducationGroupYear, pk=self.kwargs['education_group_year_id'])


class EducationGroupDetailedAchievementMixin(EducationGroupAchievementMixin):
    model = EducationGroupDetailedAchievement
    context_object_name = "education_group_detail_achievement"
    pk_url_kwarg = 'education_group_detail_achievement_pk'

    def get_education_group_achievement(self):
        return get_object_or_404(EducationGroupAchievement, pk=self.kwargs["education_group_achievement_pk"])
