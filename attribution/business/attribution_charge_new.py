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
from attribution.models import attribution_charge_new
from attribution.models.attribution_new import AttributionNew
from base.models.learning_component_year import LearningComponentYear
from base.models.learning_unit_component import LearningUnitComponent


def find_attribution_charge_new_by_learning_unit_year(learning_unit_year):
    attribution_charges = attribution_charge_new.AttributionChargeNew.objects \
        .filter(learning_component_year__learningunitcomponent__learning_unit_year=learning_unit_year) \
        .select_related('learning_component_year', 'attribution__tutor__person')
    return create_attributions_dictionary(attribution_charges)


def create_attributions_dictionary(attribution_charges):
    attributions = {}
    for attribution_charge in attribution_charges:
        key = attribution_charge.attribution.id
        attribution_dict = {"person": attribution_charge.attribution.tutor.person,
                            "function": attribution_charge.attribution.function,
                            "start_year": attribution_charge.attribution.start_year,
                            "duration": attribution_charge.attribution.duration,
                            "substitute": attribution_charge.attribution.substitute}
        attributions.setdefault(key, attribution_dict) \
            .update({attribution_charge.learning_component_year.type: attribution_charge.allocation_charge})
    return attributions


def find_attributions_for_add_partim(learning_unit_year_parent, learning_unit_year_child=None, attribution=None):
    components_year = LearningComponentYear.objects.filter(
        learningunitcomponent__learning_unit_year=learning_unit_year_child
    )
    attribution_charges = attribution_charge_new.AttributionChargeNew.objects \
        .filter(learning_component_year__learningunitcomponent__learning_unit_year=learning_unit_year_parent) \
        .select_related('learning_component_year', 'attribution__tutor__person')
    if learning_unit_year_child:
        attribution_charges = attribution_charges.\
            exclude(attribution__attributionchargenew__learning_component_year__in=components_year)
    if attribution:
        attribution_charges = attribution_charges.filter(attribution=attribution)
    return create_attributions_dictionary(attribution_charges)


def delete_attribution(attribution_pk):
    attribution = AttributionNew.objects.get(pk=attribution_pk)

    attribution_charges = attribution_charge_new.AttributionChargeNew.objects.filter(attribution=attribution_pk). \
        select_related("learning_component_year")
    components_year = [charge.learning_component_year for charge in attribution_charges]
    components = LearningUnitComponent.objects.filter(learning_component_year__in=components_year)

    for component in components:
        component.delete()

    for component_year in components_year:
        component_year.delete()

    for charge in attribution_charges:
        charge.delete()

    attribution.delete()

