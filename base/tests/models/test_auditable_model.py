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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import DatabaseError
from django.test import TestCase
from unittest.mock import patch

from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.group_element_year import GroupElementYearFactory
from osis_common.models.auditable_model import AuditableModel


class AuditableModelTest(TestCase):
    def setUp(self):
        pass

    def test_auditable_model_delete(self):
        luy = LearningUnitYearFactory()
        geys = [GroupElementYearFactory(child_leaf=luy) for i in range(20)]

        # First delete only a group
        result = geys[0].delete()
        self.assertTrue(result)

        self.assertEqual(result, [geys[0]])
        self.is_not_existing_for_orm(geys[0])

        # Now delete all the data with the learning unit
        luy.delete()
        self.is_not_existing_for_orm(luy)
        for gey in geys:
            self.is_not_existing_for_orm(gey)

    def test_auditable_model_delete_with_database_error(self):
        luy = LearningUnitYearFactory()
        geys = [GroupElementYearFactory(child_leaf=luy) for i in range(20)]

        result = None
        with patch.object(AuditableModel, 'save') as mock_method:
            mock_method.side_effect = DatabaseError("test error")

            try:
                luy.delete()
            except DatabaseError as e:
                result = e

        self.assertIsInstance(result, DatabaseError)
        self.is_existing_for_orm(luy)
        for gey in geys:
            self.is_existing_for_orm(gey)

    def is_existing_for_orm(self, obj):
        self.assertEqual(obj.__class__.objects.get(id=obj.id), obj)

    def is_not_existing_for_orm(self, obj):
        with self.assertRaises(ObjectDoesNotExist):
            obj.__class__.objects.get(id=obj.id)
