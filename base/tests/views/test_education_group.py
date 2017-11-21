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
import datetime
from unittest import mock

from django.core.urlresolvers import reverse
from django.test import TestCase, RequestFactory

from base.models.academic_calendar import AcademicCalendar
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.education_group_organization import EducationGroupOrganizationFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.group_element_year import GroupElementYearFactory


def save(self, *args, **kwargs):
    return super(AcademicCalendar, self).save()


class EducationGroupViewTestCase(TestCase):
    def setUp(self):
        today = datetime.date.today()
        self.academic_year = AcademicYearFactory(start_date=today,
                                                 end_date=today.replace(year=today.year + 1),
                                                 year=today.year)

    @mock.patch('django.contrib.auth.decorators')
    @mock.patch('base.views.layout.render')
    def test_education_groups_search(self, mock_render, mock_decorators):
        mock_decorators.login_required = lambda x: x
        mock_decorators.permission_required = lambda *args, **kwargs: lambda func: func
        request_factory = RequestFactory()
        # Create educations group year
        EducationGroupYearFactory(acronym='EDPH2', academic_year=self.academic_year)
        EducationGroupYearFactory(acronym='ARKE2A', academic_year=self.academic_year)
        EducationGroupYearFactory(acronym='HIST2A', academic_year=self.academic_year)
        request = request_factory.get(reverse('education_groups'), data={
            'acronym': 'EDPH2',
            'academic_year': self.academic_year.id,
            'type': ''  # Simulate all type
        })
        request.user = mock.Mock()

        from base.views.education_group import education_groups

        education_groups(request)
        self.assertTrue(mock_render.called)
        request, template, context = mock_render.call_args[0]
        self.assertEqual(template, 'education_groups.html')
        self.assertEqual(len(context['object_list']), 1)

    @mock.patch('django.contrib.auth.decorators')
    @mock.patch('base.views.layout.render')
    def test_education_groups_search_empty_result(self, mock_render, mock_decorators):
        from django.contrib.messages.storage.fallback import FallbackStorage

        mock_decorators.login_required = lambda x: x
        mock_decorators.permission_required = lambda *args, **kwargs: lambda func: func
        request_factory = RequestFactory()
        request = request_factory.get(reverse('education_groups'), data={
            'acronym': '',
            'academic_year': self.academic_year.id,
            'type': ''  # Simulate all type
        })
        request.user = mock.Mock()
        # Need session in order to store messages
        setattr(request, 'session', {})
        setattr(request, '_messages', FallbackStorage(request))

        from base.views.education_group import education_groups

        education_groups(request)
        self.assertTrue(mock_render.called)
        request, template, context = mock_render.call_args[0]
        self.assertEqual(template, 'education_groups.html')
        self.assertFalse(context['object_list'])
        # It should have one message ['no_result']
        self.assertEqual(len(request._messages), 1)

    @mock.patch('django.contrib.auth.decorators')
    @mock.patch('base.views.layout.render')
    @mock.patch('base.models.program_manager.is_program_manager', return_value=True)
    @mock.patch('base.models.education_group_year.find_by_id')
    def test_education_group_read(self,
                                  mock_find_by_id,
                                  mock_program_manager,
                                  mock_render,
                                  mock_decorators):
        mock_decorators.login_required = lambda x: x
        mock_decorators.permission_required = lambda *args, **kwargs: lambda func: func
        education_group_year = EducationGroupYearFactory(academic_year=self.academic_year)
        organization = EducationGroupOrganizationFactory(education_group_year=education_group_year)
        request = mock.Mock(method='GET')

        from base.views.education_group import education_group_read

        mock_find_by_id.return_value = education_group_year
        education_group_read(request, education_group_year.id)
        self.assertTrue(mock_render.called)
        request, template, context = mock_render.call_args[0]
        self.assertEqual(template, 'education_group/tab_identification.html')
        self.assertEqual(context['education_group_year'].coorganizations.first(), organization)
        self.assertEqual(context['education_group_year'].coorganizations.first().address, organization.address)

    @mock.patch('django.contrib.auth.decorators')
    @mock.patch('base.views.layout.render')
    @mock.patch('base.models.program_manager.is_program_manager', return_value=True)
    @mock.patch('base.models.education_group_year.find_by_id')
    def test_education_group_parent_read(self,
                                         mock_find_by_id,
                                         mock_program_manager,
                                         mock_render,
                                         mock_decorators):
        mock_decorators.login_required = lambda x: x
        mock_decorators.permission_required = lambda *args, **kwargs: lambda func: func
        education_group_year_child = EducationGroupYearFactory(academic_year=self.academic_year)
        education_group_year_parent = EducationGroupYearFactory(academic_year=self.academic_year)
        GroupElementYearFactory(parent=education_group_year_parent, child_branch=education_group_year_child)
        request = mock.Mock(method='GET')

        from base.views.education_group import education_group_parent_read

        mock_find_by_id.return_value = education_group_year_child
        education_group_parent_read(request, education_group_year_child.id)
        self.assertTrue(mock_render.called)
        request, template, context = mock_render.call_args[0]
        self.assertEqual(template, 'education_group/tab_identification.html')
        self.assertEqual(context['education_group_year'].parent_by_training, education_group_year_parent)

    @mock.patch('django.contrib.auth.decorators')
    @mock.patch('base.views.layout.render')
    @mock.patch('base.models.person.get_user_interface_language', return_value=True)
    def test_education_group_general_informations(self,
                                                  mock_get_user_interface_language,
                                                  mock_render,
                                                  mock_decorators):
        mock_decorators.login_required = lambda x: x
        mock_decorators.permission_required = lambda *args, **kwargs: lambda func: func
        education_group_year = EducationGroupYearFactory(academic_year=self.academic_year)
        request = mock.Mock(method='GET')

        from base.views.education_group import education_group_general_informations

        education_group_general_informations(request, education_group_year.id)
        self.assertTrue(mock_render.called)
        request, template, context = mock_render.call_args[0]
        self.assertEqual(template, 'education_group/tab_general_informations.html')

    @mock.patch('django.contrib.auth.decorators')
    @mock.patch('base.views.layout.render')
    def test_education_administrative_data(self,
                                           mock_render,
                                           mock_decorators):
        mock_decorators.login_required = lambda x: x
        mock_decorators.permission_required = lambda *args, **kwargs: lambda func: func
        education_group_year = EducationGroupYearFactory(academic_year=self.academic_year)
        request = mock.Mock(method='GET')

        from base.views.education_group import education_group_administrative_data

        education_group_administrative_data(request, education_group_year.id)
        self.assertTrue(mock_render.called)
        request, template, context = mock_render.call_args[0]
        self.assertEqual(template, 'education_group/tab_administrative_data.html')
        self.assertEqual(context['education_group_year'], education_group_year)

    def test_get_sessions_dates(self):
        from base.views.education_group import get_sessions_dates
        from base.tests.factories.session_exam_calendar import SessionExamCalendarFactory
        from base.tests.factories.academic_calendar import AcademicCalendarFactory
        from base.tests.factories.education_group_year import EducationGroupYearFactory
        from base.tests.factories.offer_year_calendar import OfferYearCalendarFactory

        sessions_quantity = 3
        an_academic_year = AcademicYearFactory()
        academic_calendar = AcademicCalendarFactory.build(academic_year=an_academic_year)
        academic_calendar.save(functions=[])
        education_group_year = EducationGroupYearFactory(academic_year=an_academic_year)
        session_exam_calendars = [SessionExamCalendarFactory(number_session=session,
                                                             academic_calendar=academic_calendar)
                                  for session in range(1, sessions_quantity + 1)]
        offer_year_calendar = OfferYearCalendarFactory(
            academic_calendar=academic_calendar,
            education_group_year=education_group_year
        )
        self.assertEquals(
            get_sessions_dates(academic_calendar.reference, education_group_year),
            {
                'session{}'.format(s): offer_year_calendar for s in range(1, sessions_quantity + 1)
            }
        )

    @mock.patch('django.contrib.auth.decorators')
    @mock.patch('base.views.layout.render')
    def test_education_content(self,
                                           mock_render,
                                           mock_decorators):
        mock_decorators.login_required = lambda x: x
        mock_decorators.permission_required = lambda *args, **kwargs: lambda func: func
        education_group_year = EducationGroupYearFactory(academic_year=self.academic_year)
        request = mock.Mock(method='GET')

        from base.views.education_group import education_group_content

        education_content(request, education_group_year.id)
        self.assertTrue(mock_render.called)
        request, template, context = mock_render.call_args[0]
        self.assertEqual(template, 'education_group/tab_content.html')
        self.assertEqual(context['education_group_year'], education_group_year)