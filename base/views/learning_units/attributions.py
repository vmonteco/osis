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
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.functional import cached_property
from django.views.generic import FormView, DeleteView

from attribution.business import attribution_charge_new
from attribution.business.attribution_charge_new import delete_attribution
from attribution.models.attribution_charge_new import AttributionChargeNew
from attribution.models.attribution_new import AttributionNew
from base.forms.learning_unit.attribution_charge_repartition import AttributionChargeRepartitionFormSet, \
    AttributionChargeNewFormSet
from base.models.enums import learning_component_year_type
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
    form_class = AttributionChargeRepartitionFormSet

    @cached_property
    def learning_unit_year_obj(self):
        return get_object_or_404(LearningUnitYear, id=self.kwargs["learning_unit_year_id"])

    @cached_property
    def parent_learning_unit_year_obj(self):
        return self.learning_unit_year_obj.parent

    @cached_property
    def attribution_new_obj(self):
        return attribution_charge_new.find_attributions_for_add_partim(self.parent_learning_unit_year_obj,
                                                                       self.learning_unit_year_obj,
                                                                       self.kwargs["attribution_id"]).popitem()[1]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["learning_unit_year"] = self.learning_unit_year_obj
        context["attribution"] = self.attribution_new_obj
        context["formset"] = context["form"]
        return context

    def get_initial(self):
        initial_data = [
            {"allocation_charge": self.attribution_new_obj.get(learning_component_year_type.LECTURING)},
            {"allocation_charge": self.attribution_new_obj.get(learning_component_year_type.PRACTICAL_EXERCISES)}
        ]
        return initial_data

    def form_valid(self, formset):
        attribution_copy = self.attribution_new_obj
        attribution_copy.id = None
        attribution_copy.save()

        types = (learning_component_year_type.LECTURING, learning_component_year_type.PRACTICAL_EXERCISES)
        for form, component_type in zip(formset, types):
            form.save(attribution_copy, self.learning_unit_year_obj, component_type)

        return super().form_valid(formset)

    def get_success_url(self):
        return reverse("learning_unit_attributions", args=[self.kwargs["learning_unit_year_id"]])


@method_decorator(login_required, name='dispatch')
class EditChargeRepartition(AjaxTemplateMixin, FormView):
    template_name = "learning_unit/add_charge_repartition.html"
    form_class = AttributionChargeNewFormSet

    @cached_property
    def learning_unit_year_obj(self):
        return get_object_or_404(LearningUnitYear, id=self.kwargs["learning_unit_year_id"])

    @cached_property
    def attribution_new_obj(self):
        return attribution_charge_new.find_attributions_for_add_partim(self.learning_unit_year_obj,
                                                                       self.kwargs["attribution_id"]).popitem()[1]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["learning_unit_year"] = self.learning_unit_year_obj
        context["attribution"] = self.attribution_new_obj
        context["formset"] = context["form"]
        return context

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs["form_kwargs"] = {
            "instances": [attributioncharge for attributioncharge in AttributionChargeNew.objects.filter(attribution=self.kwargs["attribution_id"]).order_by("learning_component_year__type")]
        }
        return form_kwargs


    def form_valid(self, formset):
        for form in formset:
            form.save()
        return super().form_valid(formset)


    def get_success_url(self):
        return reverse("learning_unit_attributions", args=[self.kwargs["learning_unit_year_id"]])


@method_decorator(login_required, name='dispatch')
class RemoveChargeRepartition(AjaxTemplateMixin, DeleteView):
    model = AttributionNew
    template_name = "learning_unit/remove_charge_repartition_confirmation.html"

    def delete(self, request, *args, **kwargs):
        delete_attribution(self.kwargs["pk"])
        success_url = self.get_success_url()
        return HttpResponseRedirect(success_url)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["learning_unit_year"] = get_object_or_404(LearningUnitYear, id=self.kwargs["learning_unit_year_id"])
        context["attribution"] = get_object_or_404(AttributionNew, pk=self.kwargs["pk"])
        return context

    def get_success_url(self):
        return reverse("learning_unit_attributions", args=[self.kwargs["learning_unit_year_id"]])
