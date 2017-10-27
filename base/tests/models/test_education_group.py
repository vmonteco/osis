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
from base.models.education_group import *

from base.tests.factories.education_group import EducationGroupFactory


class EducationGroupTest(TestCase):
    def setUp(self):
        self.education_group = EducationGroupFactory()
        self.education_group.save()

    def test_return_str_format(self):
        self.assertEqual(self.education_group.__str__(), str(self.education_group.id))

    def test_find_by_id(self):
        education_group = find_by_id(self.education_group.id)
        self.assertEqual(education_group, self.education_group)

        education_group = find_by_id(-1)
        self.assertIsNone(education_group)
