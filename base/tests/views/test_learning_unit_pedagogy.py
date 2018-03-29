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
import datetime
from unittest import mock

from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.test import TestCase, RequestFactory

from base.models.enums import entity_container_year_link_type
from base.models.enums import learning_container_year_types, organization_type
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.entity import EntityFactory
from base.tests.factories.entity_container_year import EntityContainerYearFactory
from base.tests.factories.entity_version import EntityVersionFactory
from base.tests.factories.learning_container_year import LearningContainerYearFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.organization import OrganizationFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.person_entity import PersonEntityFactory
from base.tests.factories.user import UserFactory
from base.views.learning_units.search import SUMMARY_LIST
from reference.tests.factories.country import CountryFactory
from base.tests.factories.entity_calendar import EntityCalendarFactory
from base.tests.factories.academic_calendar import AcademicCalendarFactory
from base.models.enums import academic_calendar_type
from base.tests.factories.academic_year import create_current_academic_year


class LearningUnitViewPedagogyTestCase(TestCase):
    def setUp(self):
        today = datetime.date.today()
        self.current_academic_year = AcademicYearFactory(start_date=today,
                                                         end_date=today.replace(year=today.year + 1),
                                                         year=today.year)
        self.current_academic_year = create_current_academic_year()
        self.organization = OrganizationFactory(type=organization_type.MAIN)
        self.country = CountryFactory()
        self.url = reverse('learning_units_summary')

    def test_learning_units_summary_list_no_access(self):
        request_factory = RequestFactory()
        a_user = UserFactory()
        request = request_factory.get(self.url)
        request.user = a_user
        self.client.force_login(a_user)
        from base.views.learning_units.educational_information import learning_units_summary_list
        with self.assertRaises(PermissionDenied):
            learning_units_summary_list(request)

    @mock.patch('base.views.layout.render')
    def test_learning_units_summary_list_no_entity_calendar(self, mock_render):

        request_factory = RequestFactory()

        faculty_managers_group = Group.objects.get(name='faculty_managers')
        faculty_user = UserFactory()
        faculty_user.groups.add(faculty_managers_group)
        faculty_person = PersonFactory(user=faculty_user)
        an_entity = EntityFactory(country=self.country, organization=self.organization)
        EntityVersionFactory(entity=an_entity)
        PersonEntityFactory(person=faculty_person, entity=an_entity)
        request = request_factory.get(self.url)
        request.user = faculty_user
        self._create_learning_unit_year_for_entity(an_entity)
        self.client.force_login(faculty_user)
        from base.views.learning_units.educational_information import learning_units_summary_list
        learning_units_summary_list(request)
        self.assertTrue(mock_render.called)
        request, template, context = mock_render.call_args[0]
        self.assertEqual(template, 'learning_units.html')
        self.assertEqual(context['search_type'], SUMMARY_LIST)
        self.assertEqual(len(context['learning_units']), 1)

    @mock.patch('base.views.layout.render')
    def test_learning_units_summary_list(self, mock_render):
        request_factory = RequestFactory()

        faculty_managers_group = Group.objects.get(name='faculty_managers')
        faculty_user = UserFactory()
        faculty_user.groups.add(faculty_managers_group)
        faculty_person = PersonFactory(user=faculty_user)
        an_entity = EntityFactory(country=self.country, organization=self.organization)
        now = datetime.datetime.now()
        EntityVersionFactory(entity=an_entity,
                             start_date=now,
                             end_date=datetime.datetime(now.year+1, 9, 15),
                             entity_type='INSTITUTE')

        a_person_entity = PersonEntityFactory(person=faculty_person, entity=an_entity)
        a_person_entity.save()
        request = request_factory.get(self.url)
        request.user = faculty_user
        self._create_learning_unit_year_for_entity(an_entity)
        self._create_entity_calendar(an_entity)
        self.client.force_login(faculty_user)
        from base.views.learning_units.educational_information import learning_units_summary_list
        learning_units_summary_list(request)

        self.assertTrue(mock_render.called)
        request, template, context = mock_render.call_args[0]
        self.assertEqual(template, 'learning_units.html')
        self.assertEqual(context['search_type'], SUMMARY_LIST)
        self.assertEqual(len(context['learning_units']), 1)
        self.assertTrue(context['is_faculty_manager'])

    def _create_entity_calendar(self, an_entity):
        an_academic_calendar = AcademicCalendarFactory(academic_year=self.current_academic_year,
                                                       start_date=self.current_academic_year.start_date,
                                                       end_date=self.current_academic_year.end_date,
                                                       reference=academic_calendar_type.SUMMARY_COURSE_SUBMISSION)
        EntityCalendarFactory(entity=an_entity, academic_calendar=an_academic_calendar,
                              start_date=an_academic_calendar.start_date,
                              end_date=an_academic_calendar.end_date)

    def _create_learning_unit_year_for_entity(self, an_entity):
        l_container_yr = LearningContainerYearFactory(acronym="LBIR1100",
                                                      academic_year=self.current_academic_year,
                                                      container_type=learning_container_year_types.COURSE)
        EntityContainerYearFactory(learning_container_year=l_container_yr,
                                   entity=an_entity,
                                   type=entity_container_year_link_type.REQUIREMENT_ENTITY)
        LearningUnitYearFactory(acronym="LBIR1100",
                                learning_container_year=l_container_yr,
                                academic_year=self.current_academic_year)
