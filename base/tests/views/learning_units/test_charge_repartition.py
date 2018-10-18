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
from unittest import skip
from unittest.mock import patch

from django.http import HttpResponse
from django.test import TestCase
from django.urls import reverse

from attribution.models.attribution_charge_new import AttributionChargeNew
from attribution.models.attribution_new import AttributionNew
from attribution.tests.factories.attribution_charge_new import AttributionChargeNewFactory
from attribution.tests.factories.attribution_new import AttributionNewFactory
from base.tests.factories.learning_unit_component import LearningUnitComponentFactory, \
    LecturingLearningUnitComponentFactory, PracticalLearningUnitComponentFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFullFactory, LearningUnitYearPartimFactory
from base.tests.factories.person import PersonFactory, PersonWithPermissionsFactory


@skip
class TestSelectAttributionView(TestCase):
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


@skip
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



@skip
class TestEditChargeRepartition(TestCase):
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


class TestRemoveChargeRepartition(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.learning_unit_year = LearningUnitYearFullFactory()
        cls.lecturing_unit_component = LecturingLearningUnitComponentFactory(learning_unit_year=cls.learning_unit_year)
        cls.practical_unit_component = PracticalLearningUnitComponentFactory(learning_unit_year=cls.learning_unit_year)
        cls.person = PersonWithPermissionsFactory('can_access_learningunit')

    def setUp(self):
        self.attribution = AttributionNewFactory(
            learning_container_year=self.learning_unit_year.learning_container_year
        )
        self.charge_lecturing = AttributionChargeNewFactory(
            attribution=self.attribution,
            learning_component_year=self.lecturing_unit_component.learning_component_year
        )
        self.charge_practical = AttributionChargeNewFactory(
            attribution=self.attribution,
            learning_component_year=self.practical_unit_component.learning_component_year
        )

        self.url = reverse("remove_charge_repartition", args=[self.learning_unit_year.id, self.attribution.id])
        self.client.force_login(self.person.user)

        self.patcher = patch("base.business.learning_units.perms._is_eligible_to_manage_charge_repartition",
                             return_value=True)
        self.mocked_permission_function = self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def test_login_required(self):
        self.client.logout()

        response = self.client.get(self.url)
        self.assertRedirects(response,  '/login/?next={}'.format(self.url))

    def test_template_used_with_get(self):
        response = self.client.get(self.url)

        self.mocked_permission_function.assert_called_once_with(self.learning_unit_year, self.person)
        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertTemplateUsed(response, "learning_unit/remove_charge_repartition_confirmation.html")

    def test_delete_data(self):
        response = self.client.delete(self.url)

        self.assertFalse(AttributionNew.objects.filter(id=self.attribution.id).exists())
        self.assertFalse(
            AttributionChargeNew.objects.filter(id__in=(self.charge_lecturing.id, self.charge_practical.id)).exists()
        )

    def test_delete_redirection(self):
        response = self.client.delete(self.url, follow=False)

        self.assertRedirects(response,
                             reverse("learning_unit_attributions", args=[self.learning_unit_year.id]))
