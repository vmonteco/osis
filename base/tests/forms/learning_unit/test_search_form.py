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
from base.models.enums import entity_container_year_link_type, entity_type
from base.models.learning_unit_year import LearningUnitYear
from base.tests.factories.entity_container_year import EntityContainerYearFactory
from base.tests.factories.entity_version import EntityVersionFactory
from base.tests.factories.group_element_year import GroupElementYearFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.offer_year_entity import OfferYearEntityFactory


class TestFilterIsBorrowedLearningUnitYear(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.luys_not_in_education_group = [LearningUnitYearFactory() for _ in range(3)]
        cls.luys_with_same_entity_as_education_group = \
            create_learning_unit_years_with_same_requirement_entity_and_entity_of_education_group()
        cls.luys_in_same_faculty_as_education_group = \
            create_learning_unit_years_with_requirement_entity_and_entity_of_education_group_in_same_faculty()
        cls.luys_in_different_faculty_than_education_group = \
            create_learning_unit_years_with_requirement_entity_not_in_same_faculty_than_education_group()

    def test_empty_queryset(self):
        empty_qs = LearningUnitYear.objects.none()
        result = list(filter_is_borrowed_learning_unit_year(empty_qs))
        self.assertFalse(result)

    def test_with_learning_unit_years_not_used_in_any_education_group(self):
        self.assert_filter_borrowed_luys_returns_empty_qs(self.luys_not_in_education_group)

    def test_with_learning_unit_years_when_requirement_entity_same_as_education_group(self):
        self.assert_filter_borrowed_luys_returns_empty_qs(self.luys_with_same_entity_as_education_group)

    def test_with_learning_unit_years_when_entity_for_luy_and_education_group_in_same_faculty(self):
        self.assert_filter_borrowed_luys_returns_empty_qs(self.luys_in_same_faculty_as_education_group)

    def test_with_learning_unit_when_entity_for_luy_and_education_group_in_different_faculty(self):
        qs = LearningUnitYear.objects.filter(
            pk__in=[luy.pk for luy in self.luys_in_different_faculty_than_education_group]
        )
        result = list(filter_is_borrowed_learning_unit_year(qs))
        self.assertCountEqual(result, self.luys_in_different_faculty_than_education_group)

    def assert_filter_borrowed_luys_returns_empty_qs(self, learning_unit_years):
        qs = LearningUnitYear.objects.filter(pk__in=[luy.pk for luy in learning_unit_years])
        result = list(filter_is_borrowed_learning_unit_year(qs))
        self.assertFalse(result)


def create_learning_unit_years_with_same_requirement_entity_and_entity_of_education_group():
    learning_unit_years = [LearningUnitYearFactory() for _ in range(3)]
    for luy in learning_unit_years:
        entity_container_year = EntityContainerYearFactory(
            learning_container_year=luy.learning_container_year,
            type=entity_container_year_link_type.REQUIREMENT_ENTITY
        )
        offer_year_entity = OfferYearEntityFactory(entity=entity_container_year.entity)
        group_element_year = GroupElementYearFactory(child_branch=offer_year_entity.education_group_year,
                                                     child_leaf=luy)
    return learning_unit_years


def create_learning_unit_years_with_requirement_entity_and_entity_of_education_group_in_same_faculty():
    learning_unit_years = [LearningUnitYearFactory() for _ in range(3)]
    for luy in learning_unit_years:
        entity_container_year = EntityContainerYearFactory(
            learning_container_year=luy.learning_container_year,
            type=entity_container_year_link_type.REQUIREMENT_ENTITY
        )
        entity_version = EntityVersionFactory(entity=entity_container_year.entity,
                                              entity_type=entity_type.SCHOOL)
        parent_entity_version = EntityVersionFactory(entity=entity_version.parent,
                                                     parent=None,
                                                     entity_type=entity_type.FACULTY)
        offer_year_entity = OfferYearEntityFactory(entity=entity_version.parent)
        group_element_year = GroupElementYearFactory(child_branch=offer_year_entity.education_group_year,
                                                     child_leaf=luy)
    return learning_unit_years

def create_learning_unit_years_with_requirement_entity_not_in_same_faculty_than_education_group():
    learning_unit_years = [LearningUnitYearFactory() for _ in range(3)]
    for luy in learning_unit_years:
        entity_container_year = EntityContainerYearFactory(
            learning_container_year=luy.learning_container_year,
            type=entity_container_year_link_type.REQUIREMENT_ENTITY
        )
        EntityVersionFactory(entity=entity_container_year.entity, entity_type=entity_type.FACULTY, parent=None)
        offer_year_entity = OfferYearEntityFactory()
        EntityVersionFactory(entity=offer_year_entity.entity, entity_type=entity_type.FACULTY, parent=None)
        group_element_year = GroupElementYearFactory(child_branch=offer_year_entity.education_group_year,
                                                     child_leaf=luy)

        offer_year_entity = OfferYearEntityFactory()
        EntityVersionFactory(entity=offer_year_entity.entity, entity_type=entity_type.FACULTY, parent=None)
        group_element_year = GroupElementYearFactory(child_branch=offer_year_entity.education_group_year,
                                                     child_leaf=luy)
    return learning_unit_years