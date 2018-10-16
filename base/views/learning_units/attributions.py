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
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic import FormView

from attribution.business import attribution_charge_new
from base.forms.learning_unit.attribution_charge_repartition import AttributionChargeRepartitionForm
from base.models.learning_unit_year import LearningUnitYear
from base.views import layout
from base.views.mixins import AjaxTemplateMixin


@login_required
def add_partim_attribution(request, learning_unit_year_id):
    partim_learning_unit_year = get_object_or_404(LearningUnitYear, id=learning_unit_year_id)
    full_learning_unit_year = partim_learning_unit_year.parent
    context = {}
    context["attributions"] = attribution_charge_new.find_attributions_for_add_partim(full_learning_unit_year,
                                                                                      partim_learning_unit_year)
    context["learning_unit_year"] = partim_learning_unit_year
    return layout.render(request, "learning_unit/add_attribution.html", context)


@method_decorator(login_required, name='dispatch')
class AddChargeRepartition(AjaxTemplateMixin, FormView):
    template_name = "learning_unit/add_charge_repartition.html"
    form_class = AttributionChargeRepartitionForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["learning_unit_year"] = get_object_or_404(LearningUnitYear, id=self.kwargs["learning_unit_year_id"])
        return context