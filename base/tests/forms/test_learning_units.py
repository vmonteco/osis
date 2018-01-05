##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2017 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django.test import TestCase
from django.utils import timezone
from unittest.mock import patch

from base.business.learning_unit_year_with_context import is_service_course
from base.forms.common import TooManyResultsException
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.learning_container_year import LearningContainerYearFactory
from base.tests.factories.entity_container_year import EntityContainerYearFactory
from base.tests.factories.entity_version import EntityVersionFactory
from base.models.enums import entity_container_year_link_type, entity_type
from reference.tests.factories.country import CountryFactory
from base.forms import learning_units


class TestLearningUnitForm(TestCase):
    def setUp(self):
        self.country = CountryFactory()
        self.academic_yr = AcademicYearFactory(year=timezone.now().year)
        self.start_date = self.academic_yr.start_date
        self.end_date = self.academic_yr.end_date
        """
        Create three containers:
        LC0, LC1 and LC2.
        """
        self.list_lu_container_year = [
            LearningContainerYearFactory(acronym="LC%d" % container,
                                         academic_year=self.academic_yr)
            for container in range(3)
        ]

        """
        Create the most simple Learning Units list:
        which is one Learning Unit per Container.
        So in this case, three Learning Units are instanciated:
        LUY0, LUY1 and LUY2.
        """
        self.list_lu_year = [
            LearningUnitYearFactory(acronym="LUY%d" % i,
                                    learning_container_year=container,
                                    academic_year=self.academic_yr)
            for i, container in enumerate(self.list_lu_container_year)
        ]

        """
        Create a list of entities.
        One of them must have a reference to another entity :
        the School entity 'MATH' has the Faculty entity 'SC' as parent.
        """
        meca_faculty = self._create_entity_version(entity_type=entity_type.FACULTY,
                                                   acronym="MECA_FACULTY")

        elme_faculty = self._create_entity_version(entity_type=entity_type.FACULTY,
                                            acronym="ELME_FACULTY",
                                            start_date=self.start_date,
                                            end_date=self.end_date)
        self.list_entity_version = [
            self._create_entity_version(entity_type=entity_type.SCHOOL,
                                 acronym="MECA",
                                 parent=meca_faculty.entity),
            self._create_entity_version(entity_type=entity_type.SCHOOL,
                                 acronym="ELME",
                                 parent=elme_faculty.entity)
        ]

        evf_parent = self._create_entity_version(entity_type=entity_type.FACULTY,
                                          acronym="SC")

        evf_child = self._create_entity_version(entity_type=entity_type.SCHOOL,
                                         acronym="MATH",
                                         parent=evf_parent.entity)

        self.list_entity_version.append(evf_parent)
        self.list_entity_version.append(evf_child)

        """
        Associate the entities to the Learning Units.
        The last Learning Unit LUY2 must be associated with an entity which has a related parent.
        The associations are:
            1. LUY0 -associated to LC0- has 'MECA' for REQUIREMENT Entity
            2. LUY0 -associated to LC0- has 'ELME' for ALLOCATION Entity
            3. LUY1 -associated to LC1- has 'SC' for REQUIREMENT Entity
            4. LUY1 -associated to LC1- has 'MECA' for ALLOCATION Entity
            5. LUY2 -associated to LC2- has 'SC' for REQUIREMENT Entity
            6. LUY2 -associated to LC2- has 'MATH' for ALLOCATION Entity
        """
        self.list_entity_container_year = [
            EntityContainerYearFactory(
                entity=self.list_entity_version[0].entity,
                learning_container_year=self.list_lu_container_year[0],
                type=entity_container_year_link_type.REQUIREMENT_ENTITY),
            EntityContainerYearFactory(
                entity=self.list_entity_version[1].entity,
                learning_container_year=self.list_lu_container_year[0],
                type=entity_container_year_link_type.ALLOCATION_ENTITY),
            EntityContainerYearFactory(
                entity=self.list_entity_version[2].entity,
                learning_container_year=self.list_lu_container_year[1],
                type=entity_container_year_link_type.REQUIREMENT_ENTITY),
            EntityContainerYearFactory(
                entity=self.list_entity_version[0].entity,
                learning_container_year=self.list_lu_container_year[1],
                type=entity_container_year_link_type.ALLOCATION_ENTITY),
            EntityContainerYearFactory(
                entity=self.list_entity_version[2].entity,
                learning_container_year=self.list_lu_container_year[2],
                type=entity_container_year_link_type.REQUIREMENT_ENTITY),
            EntityContainerYearFactory(
                entity=self.list_entity_version[3].entity,
                learning_container_year=self.list_lu_container_year[2],
                type=entity_container_year_link_type.ALLOCATION_ENTITY)
        ]

    def test_is_service_course(self):
        self.assertTrue(
            is_service_course(self.academic_yr, self.list_entity_version[0], self.list_entity_version[1])
        )

    def test_is_not_service_course(self):
        self.assertFalse(
            is_service_course(self.academic_yr, self.list_entity_version[2], self.list_entity_version[3])
        )

    def get_valid_data(self):
        return {
            "academic_year_id": self.academic_yr.pk,
            "acronym": "LDROI1001"
        }

    @patch("base.models.learning_unit_year.count_search_results")
    def test_case_maximum_results_reached(self, mock_count):
        mock_count.return_value = learning_units.MAX_RECORDS + 1
        form = learning_units.LearningUnitYearForm(data=self.get_valid_data())
        self.assertRaises(TooManyResultsException, form.is_valid)

    def test_get_service_courses_by_empty_requirement_and_allocation_entity(self):
        form_data = {}

        form = learning_units.LearningUnitYearForm(form_data, service_course_search=True)
        form.is_valid()
        self.assertTrue(form.is_valid())
        self.assertEqual(form.get_activity_learning_units(), [self.list_lu_year[0], self.list_lu_year[1]])

    def test_get_service_courses_by_requirement_acronym(self):
        form_data = {
            "requirement_entity_acronym": self.list_entity_version[0].acronym
        }

        form = learning_units.LearningUnitYearForm(form_data, service_course_search=True)
        form.is_valid()
        self.assertTrue(form.is_valid())
        self.assertEqual(form.get_activity_learning_units(), [self.list_lu_year[0]])

    def test_get_service_courses_by_allocation_acronym(self):
        form_data = {
            "allocation_entity_acronym": self.list_entity_version[1].acronym
        }

        form = learning_units.LearningUnitYearForm(form_data, service_course_search=True)
        form.is_valid()
        self.assertTrue(form.is_valid())
        self.assertEqual(form.get_activity_learning_units(), [self.list_lu_year[0]])

    def test_get_service_courses_by_requirement_and_allocation_acronym(self):
        form_data = {
            "requirement_entity_acronym": self.list_entity_version[0].acronym,
            "allocation_entity_acronym": self.list_entity_version[1].acronym
        }

        form = learning_units.LearningUnitYearForm(form_data, service_course_search=True)
        form.is_valid()
        self.assertTrue(form.is_valid())
        self.assertEqual(len(form.get_activity_learning_units()), 1)

    def test_get_service_courses_by_requirement_and_allocation_acronym_within_same_faculty(self):
        form_data = {
            "requirement_entity_acronym": self.list_entity_version[2].acronym,
            "allocation_entity_acronym": self.list_entity_version[3].acronym
        }

        form = learning_units.LearningUnitYearForm(form_data, service_course_search=True)
        form.is_valid()
        self.assertTrue(form.is_valid())
        self.assertEqual(form.get_activity_learning_units(), [])

    def _create_entity_version(self, **kwargs):
        start_date = kwargs.pop('start_date', self.start_date)
        end_date = kwargs.pop('end_date', self.end_date)

        return EntityVersionFactory(start_date=start_date, end_date=end_date, **kwargs)
