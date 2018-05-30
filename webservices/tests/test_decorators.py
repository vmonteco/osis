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
from unittest.mock import Mock

from django.http import HttpRequest, Http404
from django.test import TestCase

from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from webservices.views import get_cleaned_parameters


class GetCleanedParametersDecorator_TestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.academic_year = AcademicYearFactory()
        self.education_group_year = EducationGroupYearFactory(
            academic_year=self.academic_year
        )
        self.request = Mock()
        self.mocked_function = Mock(return_value='mocked')

    def test_fail_language(self):
        type_acronym, year, language, acronym = \
            'acronym', self.academic_year.year, 'it', self.education_group_year.acronym

        decorator = get_cleaned_parameters(type_acronym=type_acronym)

        decorated_function = decorator(self.mocked_function)

        with self.assertRaises(Http404):
            result = decorated_function(self.request, year, language, acronym)


    def test_works_fine(self):
        year, language = self.academic_year.year, 'fr'

        for type_acronym in ('acronym', 'partial'):
            with self.subTest(type_acronym=type_acronym):
                education_group_year = EducationGroupYearFactory(academic_year=self.academic_year)
                decorator = get_cleaned_parameters(type_acronym)

                decorated_function = decorator(self.mocked_function)

                acronym = education_group_year.acronym if type_acronym == 'acronym' else education_group_year.partial_acronym

                result = decorated_function(self.request, year, language, acronym)
                self.assertTrue(self.mocked_function.called)
                self.assertEqual(result, 'mocked')
