##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2018 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.contrib.auth.models import Group
from django.http import Http404
from django.test import TestCase

from base.business.institution.perms import can_user_edit_educational_information_submission_dates_for_entity
from base.models.person import FACULTY_MANAGER_GROUP
from base.tests.factories.entity import EntityFactory
from base.tests.factories.person_entity import PersonEntityFactory
from base.tests.factories.user import UserFactory


class TestUserCanEditEntityCalendarEducationalInformation(TestCase):
    @classmethod
    def setUpTestData(cls):
        person_entity = PersonEntityFactory()
        cls.user = person_entity.person.user
        cls.entity = person_entity.entity

        cls.user.groups.add(Group.objects.get(name=FACULTY_MANAGER_GROUP))

        cls.user_not_faculty_manager = PersonEntityFactory(entity=cls.entity).person.user

        cls.user_with_no_person = UserFactory()

        cls.entity_not_linked_to = EntityFactory()

    def test_when_user_not_linked_to_person(self):
        with self.assertRaises(Http404):
            can_user_edit_educational_information_submission_dates_for_entity(self.user_with_no_person, self.entity)

    def test_when_not_faculty_manager(self):
        can_user_edit = can_user_edit_educational_information_submission_dates_for_entity(self.user_not_faculty_manager,
                                                                                          self.entity)
        self.assertFalse(can_user_edit)

    def test_when_faculty_manager_but_not_linked_to_entity(self):
        can_user_edit = can_user_edit_educational_information_submission_dates_for_entity(self.user,
                                                                                          self.entity_not_linked_to)
        self.assertFalse(can_user_edit)

    def test_when_faculty_manager_and_linked_to_entity(self):
        can_user_edit = can_user_edit_educational_information_submission_dates_for_entity(self.user,
                                                                                          self.entity)
        self.assertTrue(can_user_edit)



