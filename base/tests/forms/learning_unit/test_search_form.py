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

from base.forms.learning_unit.search_form import filter_is_borrowed_learning_unit_year
from base.models.enums import entity_container_year_link_type
from base.models.learning_unit_year import LearningUnitYear
from base.tests.factories.entity_container_year import EntityContainerYearFactory
from base.tests.factories.group_element_year import GroupElementYearFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.offer_year_entity import OfferYearEntityFactory


class TestFilterIsBorrowedLearningUnitYear(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.luys_not_in_education_group = [LearningUnitYearFactory() for x in range(4)]
        cls.luys_with_same_entity = \
            create_learning_unit_years_with_same_requirement_entity_and_entity_of_education_group()

    def test_empty_queryset(self):
        empty_qs = LearningUnitYear.objects.none()
        result = filter_is_borrowed_learning_unit_year(empty_qs)
        self.assertFalse(result)

    def test_with_one_learning_unit_year_not_used_in_any_education_group(self):
        qs = LearningUnitYear.objects.filter(pk=self.luys_not_in_education_group[0].pk)
        result = filter_is_borrowed_learning_unit_year(qs)
        self.assertFalse(result)

    def test_with_multiple_learning_unit_years_not_used_in_any_education_group(self):
        qs = LearningUnitYear.objects.filter(pk__in=[luy.pk for luy in self.luys_not_in_education_group])
        result = filter_is_borrowed_learning_unit_year(qs)
        self.assertFalse(result)

    def test_with_one_learning_unit_year_when_requirement_entity_same_as_education_group(self):
        qs = LearningUnitYear.objects.filter(pk=self.luys_with_same_entity[0].pk)
        result = filter_is_borrowed_learning_unit_year(qs)
        self.assertFalse(result)

    def test_with_multiple_learning_unit_years_when_requirement_entity_same_as_education_group(self):
        qs = LearningUnitYear.objects.filter(pk__in=[luy.pk for luy in self.luys_with_same_entity])
        result = filter_is_borrowed_learning_unit_year(qs)
        self.assertFalse(result)


def create_learning_unit_years_with_same_requirement_entity_and_entity_of_education_group():
    learning_unit_years = [LearningUnitYearFactory() for _ in range(4)]
    for luy in learning_unit_years:
        entity_container_year = EntityContainerYearFactory(
            learning_container_year=luy.learning_container_year,
            type=entity_container_year_link_type.REQUIREMENT_ENTITY
        )
        offer_year_entity = OfferYearEntityFactory(entity=entity_container_year.entity)
        group_element_year = GroupElementYearFactory(child_branch=offer_year_entity.education_group_year,
                                                     child_leaf=luy)
    return learning_unit_years