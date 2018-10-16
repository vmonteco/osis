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
from django.forms import ModelForm

from attribution.models.attribution_charge_new import AttributionChargeNew
from base.models.learning_component_year import LearningComponentYear
from base.models.learning_unit_component import LearningUnitComponent


class AttributionChargeRepartitionForm(ModelForm):
    class Meta:
        model = AttributionChargeNew
        fields = ["allocation_charge"]

    def save(self, attribution_new_obj, luy_obj, component_type):
        attribution_charge_obj = super().save(commit=False)

        learning_component_year = LearningComponentYear(
            learning_container_year=luy_obj.learning_container_year,
            type=component_type
        )
        learning_component_year.save()

        attribution_charge_obj.attribution = attribution_new_obj
        attribution_charge_obj.learning_component_year = learning_component_year
        attribution_charge_obj.save()

        learning_unit_component = LearningUnitComponent(
            learning_unit_year=luy_obj,
            learning_component_year=learning_component_year,
            type=component_type
        )
        learning_unit_component.save()

        return attribution_charge_obj
