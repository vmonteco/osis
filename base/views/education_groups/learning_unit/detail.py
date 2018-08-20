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
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic import DetailView

from base import models as mdl
from base.models.education_group_year import EducationGroupYear
from base.models.learning_unit_year import LearningUnitYear
from base.models.person import Person


@method_decorator(login_required, name='dispatch')
class LearningUnitGenericDetailView(PermissionRequiredMixin, DetailView):
    model = LearningUnitYear
    context_object_name = "learning_unit_year"
    pk_url_kwarg = 'learning_unit_year_id'

    permission_required = 'base.can_access_education_group'
    raise_exception = True

    def get_person(self):
        return get_object_or_404(Person, user=self.request.user)

    def get_root(self):
        return get_object_or_404(EducationGroupYear, pk=self.kwargs.get("root_id"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['person'] = self.get_person()
        context['root'] = self.get_root()
        context['root_id'] = self.kwargs.get("root_id")
        context['parent'] = self.get_root()

        context['group_to_parent'] = self.request.GET.get("group_to_parent") or '0'
        return context


class LearningUnitUtilization(LearningUnitGenericDetailView):
    template_name = "education_group/learning_unit/tab_utilization.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["group_element_years"] = mdl.group_element_year.find_by_child_leaf(self.object).select_related("parent")
        return context
