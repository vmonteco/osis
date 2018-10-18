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

from django.test import TestCase
from django.utils import timezone

from attribution.business.attribution_charge_new import find_attribution_charge_new_by_learning_unit_year_as_dict, \
    delete_attribution
from attribution.models.attribution_charge_new import AttributionChargeNew
from attribution.models.attribution_new import AttributionNew
from attribution.tests.factories.attribution_charge_new import AttributionChargeNewFactory
from attribution.tests.factories.attribution_new import AttributionNewFactory
from base.models.enums import learning_unit_year_subtypes, learning_component_year_type
from base.models.learning_component_year import LearningComponentYear
from base.models.learning_unit_component import LearningUnitComponent
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.learning_unit_component import LearningUnitComponentFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory


class TestAttributionChargeNew(TestCase):
    def setUp(self):
        self.academic_year = AcademicYearFactory(year=timezone.now().year)
        self.l_unit_1 = LearningUnitYearFactory(acronym="LBIR1212", academic_year=self.academic_year,
                                                subtype=learning_unit_year_subtypes.FULL)
        component = LearningUnitComponentFactory(learning_unit_year=self.l_unit_1)
        self.attribution_charge_news = [
            AttributionChargeNewFactory(learning_component_year=component.learning_component_year) for _ in range(5)
        ]

    def test_find_attribution_charge_new_by_learning_unit_year(self):
        result = find_attribution_charge_new_by_learning_unit_year_as_dict(self.l_unit_1)
        self.assertEqual(len(result), 5)



class TestDeleteAttribution(TestCase):
    def setUp(self):
        self.luy = LearningUnitYearFactory()
        component_types = (learning_component_year_type.LECTURING, learning_component_year_type.PRACTICAL_EXERCISES)
        self.charges = []
        self.components = []
        self.attribution_obj = AttributionNewFactory()
        for component_type in component_types:
            attribution_charge_new_obj = AttributionChargeNewFactory(
                learning_component_year__learning_container_year=self.luy.learning_container_year,
                learning_component_year__type=component_type,
                attribution=self.attribution_obj
            )
            learning_unit_component = LearningUnitComponentFactory(
                learning_component_year=attribution_charge_new_obj.learning_component_year,
                learning_unit_year=self.luy,
                type=component_type
            )
            self.charges.append(attribution_charge_new_obj)
            self.components.append(learning_unit_component)


    def test_should_delete_learning_unit_component(self):
        delete_attribution(self.attribution_obj.pk)

        self.assertFalse(
            LearningUnitComponent.objects.filter(learning_unit_year=self.luy).exists()
        )

    def test_should_delete_learning_component_year(self):
        delete_attribution(self.attribution_obj.pk)

        self.assertFalse(
            LearningComponentYear.objects.filter(learning_container_year=self.luy.learning_container_year).exists()
        )

    def test_should_delete_attribution_charge_new_obj(self):
        delete_attribution(self.attribution_obj.pk)

        self.assertFalse(
            AttributionChargeNew.objects.filter(attribution=self.attribution_obj).exists()
        )

    def test_should_delete_attribution_new_obj(self):
        delete_attribution(self.attribution_obj.pk)

        self.assertFalse(
            AttributionNew.objects.filter(pk=self.attribution_obj.pk).exists()
        )



