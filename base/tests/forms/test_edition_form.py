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

from base.business.learning_unit_year_with_context import get_with_context
from base.forms.learning_unit.edition_volume import VolumeEditionForm
from base.tests.factories.business.learning_units import GenerateContainer, GenerateAcademicYear


class TestVolumeEditionForm(TestCase):
    def setUp(self):
        self.start_year = 2010
        self.end_year = 2020
        self.generated_ac_years= GenerateAcademicYear(self.start_year, self.end_year)
        self.generated_container = GenerateContainer(self.start_year, self.end_year)
        self.first_learning_unit_year = self.generated_container.generated_container_years[0].learning_unit_year_full

    def test_get_volume_form(self):
        learning_unit_with_context = get_with_context(
            learning_container_year_id=self.first_learning_unit_year.learning_container_year)[0]

        for component_values in learning_unit_with_context.components.values():
            form = VolumeEditionForm(component_values=component_values, entities=learning_unit_with_context.entities)

            print(form.fields)

