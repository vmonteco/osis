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
from django.urls import reverse

from attribution.tests.factories.attribution_charge_new import AttributionChargeNewFactory
from base.tests.factories.learning_unit_component import LearningUnitComponentFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFullFactory, LearningUnitYearPartimFactory
from base.tests.factories.person import PersonFactory


class TestAddPartimAttribution(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.learning_unit_year_parent = LearningUnitYearFullFactory()
        cls.learning_unit_year_child = LearningUnitYearPartimFactory(
            learning_container_year=cls.learning_unit_year_parent.learning_container_year
        )

        cls.attributions = [cls.create_attribution_charge_for_specific_learning_unit_year(cls.learning_unit_year_parent)
                            for _ in range(3)]

        cls.person = PersonFactory()
        cls.url = reverse("add_partim_attribution", args=[cls.learning_unit_year_child.id])

    @staticmethod
    def create_attribution_charge_for_specific_learning_unit_year(luy):
        attribution_charge_new = AttributionChargeNewFactory(
            learning_component_year__learning_container_year=luy.learning_container_year
        )
        learning_unit_component = LearningUnitComponentFactory(
            learning_component_year=attribution_charge_new.learning_component_year,
            learning_unit_year=luy
        )
        return attribution_charge_new

    def setUp(self):
        self.client.force_login(self.person.user)

    def test_login_required(self):
        self.client.logout()

        response = self.client.get(self.url)
        self.assertRedirects(response,  '/login/?next={}'.format(self.url))

    def test_template_used(self):
        response = self.client.get(self.url)

        self.assertTemplateUsed(response, "learning_unit/add_attribution.html")

    def test_should_give_all_attributions_of_parent_if_no_attribution_in_child(self):
        response = self.client.get(self.url)

        context = response.context
        self.assertEqual(
            len(context["attributions"]),
            len(self.attributions)
        )

    def test_should_not_show_attributions_of_child(self):
        attribution = AttributionChargeNewFactory(
            attribution=self.attributions[0].attribution,
            learning_component_year__learning_container_year=self.learning_unit_year_child.learning_container_year
        )

        LearningUnitComponentFactory(
            learning_unit_year=self.learning_unit_year_child,
            learning_component_year=attribution.learning_component_year
        )

        response = self.client.get(self.url)

        context = response.context
        self.assertEqual(
            len(context["attributions"]),
            len(self.attributions[1:])
        )


class TestAddChargeRepartition(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.learning_unit_year_parent = LearningUnitYearFullFactory()
        cls.learning_unit_year_child = LearningUnitYearPartimFactory(
            learning_container_year=cls.learning_unit_year_parent.learning_container_year
        )

        cls.attribution = cls.create_attribution_charge_for_specific_learning_unit_year(cls.learning_unit_year_parent)

        cls.person = PersonFactory()
        cls.url = reverse("add_charge_repartition", args=[cls.learning_unit_year_child.id, cls.attribution.id])

    @staticmethod
    def create_attribution_charge_for_specific_learning_unit_year(luy):
        attribution_charge_new = AttributionChargeNewFactory(
            learning_component_year__learning_container_year=luy.learning_container_year
        )
        learning_unit_component = LearningUnitComponentFactory(
            learning_component_year=attribution_charge_new.learning_component_year,
            learning_unit_year=luy
        )
        return attribution_charge_new

    def setUp(self):
        self.client.force_login(self.person.user)

    def test_login_required(self):
        self.client.logout()

        response = self.client.get(self.url)
        self.assertRedirects(response,  '/login/?next={}'.format(self.url))

    def test_template_used(self):
        response = self.client.get(self.url)

        self.assertTemplateUsed(response, "learning_unit/add_charge_repartition.html")
