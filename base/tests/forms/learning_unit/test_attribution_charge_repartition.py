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

from attribution.tests.factories.attribution import AttributionNewFactory
from base.forms.learning_unit.attribution_charge_repartition import AttributionChargeRepartitionForm
from base.models.enums import learning_component_year_type, component_type
from base.models.learning_unit_component import LearningUnitComponent
from base.tests.factories.learning_unit_year import LearningUnitYearFactory

ALLOCATION_CHARGE_VALUE = 10
class TestAttributionChargeRepartitionForm(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.attribution = AttributionNewFactory()
        cls.learning_unit_year = LearningUnitYearFactory()
        cls.form_data = {
            "allocation_charge": ALLOCATION_CHARGE_VALUE
        }

    def test_save(self):
        form = AttributionChargeRepartitionForm(self.form_data)

        self.assertTrue(form.is_valid())
        attribution_charge_obj = form.save(self.attribution, self.learning_unit_year,
                                           learning_component_year_type.LECTURING)

        self.assertIsNotNone(attribution_charge_obj.id)
        self.assertEqual(attribution_charge_obj.attribution,
                         self.attribution)
        self.assertEqual(attribution_charge_obj.allocation_charge,
                         ALLOCATION_CHARGE_VALUE)

        self.assertIsNotNone(attribution_charge_obj.learning_component_year.id)
        self.assertEqual(attribution_charge_obj.learning_component_year.type,
                         learning_component_year_type.LECTURING)
        self.assertEqual(attribution_charge_obj.learning_component_year.learning_container_year,
                         self.learning_unit_year.learning_container_year)


        learning_unit_component = LearningUnitComponent.objects.get(
            learning_unit_year=self.learning_unit_year,
            learning_component_year=attribution_charge_obj.learning_component_year,
            type=learning_component_year_type.LECTURING
        )
