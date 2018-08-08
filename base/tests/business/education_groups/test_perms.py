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
import datetime

from django.test import TestCase

from base.business.education_groups.perms import is_education_group_creation_period_opened, check_permission, \
    check_authorized_type
from base.models.enums import academic_calendar_type
from base.models.enums.education_group_categories import TRAINING
from base.tests.factories.academic_calendar import AcademicCalendarFactory
from base.tests.factories.authorized_relationship import AuthorizedRelationshipFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.person import PersonFactory, PersonWithPermissionsFactory, CentralManagerFactory


class TestPerms(TestCase):
    def test_has_person_the_right_to_add_education_group(self):
        person_without_right = PersonFactory()
        self.assertFalse(check_permission(person_without_right, "base.add_educationgroup"))

        person_with_right = PersonWithPermissionsFactory("add_educationgroup")
        self.assertTrue(check_permission(person_with_right, "base.add_educationgroup"))

    def test_is_education_group_creation_period_opened(self):
        person = PersonFactory()
        today = datetime.date.today()

        closed_period = AcademicCalendarFactory(start_date=today + datetime.timedelta(days=1),
                                                end_date=today + datetime.timedelta(days=3),
                                                reference=academic_calendar_type.EDUCATION_GROUP_EDITION)

        self.assertFalse(is_education_group_creation_period_opened())

        opened_period = closed_period
        opened_period.start_date = today
        opened_period.save()
        self.assertTrue(is_education_group_creation_period_opened())

    def is_person_central_manager(self):
        person = PersonFactory()
        self.assertFalse(person.is_central_manager())

        central_manager = CentralManagerFactory()
        self.assertTrue(central_manager.is_central_manager())

    def test_check_unauthorized_type(self):
        education_group = EducationGroupYearFactory()
        result = check_authorized_type(education_group, TRAINING)
        self.assertFalse(result)

    def test_check_authorized_type(self):
        education_group = EducationGroupYearFactory()
        AuthorizedRelationshipFactory(parent_type=education_group.education_group_type)
        result = check_authorized_type(education_group, TRAINING)
        self.assertTrue(result)

    def test_check_authorized_type_without_parent(self):
        result = check_authorized_type(None, TRAINING)
        self.assertTrue(result)
