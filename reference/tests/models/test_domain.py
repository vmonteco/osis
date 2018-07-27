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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django.db.models.query import QuerySet
from django.test import TestCase

from reference.models import domain
from reference.models.enums import domain_type
from reference.tests.factories.domain import DomainFactory


class TestDomainFindByType(TestCase):
    def setUp(self):
        self.domain = DomainFactory(type=domain_type.UNIVERSITY)

    def test_find_by_type_case_not_found(self):
        result = domain.find_by_type(type=domain_type.UNKNOWN)
        self.assertIsInstance(result, QuerySet)
        self.assertFalse(result.count())

    def test_find_by_type_case_found(self):
        result = domain.find_by_type(type=domain_type.UNIVERSITY)
        self.assertIsInstance(result, QuerySet)
        self.assertEqual(result.count(), 1)
        self.assertEqual(result[0], self.domain)
