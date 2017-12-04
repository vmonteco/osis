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
from unittest import mock

from django.contrib.messages.api import get_messages
from django.contrib import messages
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.test import TestCase, RequestFactory
from base.models.enums import learning_unit_year_subtypes
from base.models.learning_container import LearningContainer
from base.models.learning_unit_year import LearningUnitYear
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.learning_unit import LearningUnitFactory
from base.tests.factories.learning_unit_enrollment import LearningUnitEnrollmentFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.learning_class_year import LearningClassYearFactory
from base.tests.factories.learning_component_year import LearningComponentYearFactory
from base.tests.factories.learning_container_year import LearningContainerYearFactory
from base.tests.factories.learning_unit_component import LearningUnitComponentFactory
from django.utils.translation import ugettext_lazy as _


class LearningUnitDelete(TestCase):

    def create_learning_unit_years_and_dependencies(self):
        l1 = LearningUnitFactory()
        academic_years = [AcademicYearFactory(year=2000 + y) for y in range(4)]

        lcy2 = LearningContainerYearFactory()
        learning_unit_years = [LearningUnitYearFactory(learning_unit=l1, academic_year=academic_years[y]) for y in
                               range(4)]
        learning_unit_years[1].learning_container_year = lcy2
        learning_unit_years[1].subtype = learning_unit_year_subtypes.FULL
        learning_unit_years[1].save()

        lcomponent = LearningComponentYearFactory()

        LearningClassYearFactory(learning_component_year=lcomponent)
        LearningClassYearFactory(learning_component_year=lcomponent)
        LearningUnitComponentFactory(learning_unit_year=learning_unit_years[1],
                                     learning_component_year=lcomponent)
        return learning_unit_years

    @mock.patch('django.contrib.auth.decorators')
    @mock.patch('base.views.layout.render')
    def test_delete_from_given_learning_unit_year_case_success(self, mock_render, mock_decorators):
        mock_decorators.login_required = lambda x: x
        mock_decorators.permission_required = lambda *args, **kwargs: lambda func: func

        learning_unit_years = self.create_learning_unit_years_and_dependencies()

        from base.views.learning_unit_deletion import delete_from_given_learning_unit_year

        request_factory = RequestFactory()

        request = request_factory.get(reverse(delete_from_given_learning_unit_year, args=[learning_unit_years[1].id]))
        request.user = mock.Mock()

        delete_from_given_learning_unit_year(request, learning_unit_years[1].id)

        self.assertTrue(mock_render.called)
        request, template, context = mock_render.call_args[0]

        self.assertEqual(_('msg_warning_delete_learning_unit') % learning_unit_years[1], context['title'])

        # click on accept button
        request = request_factory.post(reverse(delete_from_given_learning_unit_year, args=[learning_unit_years[1].id]))
        request.user = mock.Mock()
        setattr(request, 'session', 'session')
        setattr(request, '_messages', FallbackStorage(request))

        delete_from_given_learning_unit_year(request, learning_unit_years[1].id)

        msg_level = [m.level for m in get_messages(request)]
        msg = [m.message for m in get_messages(request)]
        self.assertEqual(len(msg), 4)
        self.assertIn(messages.SUCCESS, msg_level)

        with self.assertRaises(ObjectDoesNotExist):
            LearningUnitYear.objects.get(id=learning_unit_years[1].id)

        with self.assertRaises(ObjectDoesNotExist):
            LearningUnitYear.objects.get(id=learning_unit_years[2].id)

        with self.assertRaises(ObjectDoesNotExist):
            LearningUnitYear.objects.get(id=learning_unit_years[3].id)

        self.assertIsNotNone(LearningUnitYear.objects.get(id=learning_unit_years[0].id))

    @mock.patch('django.contrib.auth.decorators')
    @mock.patch('base.views.layout.render')
    def test_delete_all_learning_units_year_case_success(self, mock_render, mock_decorators):
        mock_decorators.login_required = lambda x: x
        mock_decorators.permission_required = lambda *args, **kwargs: lambda func: func

        learning_unit_years = self.create_learning_unit_years_and_dependencies()
        learning_unit = learning_unit_years[0].learning_unit

        from base.views.learning_unit_deletion import delete_all_learning_units_year

        request_factory = RequestFactory()

        request = request_factory.get(reverse(delete_all_learning_units_year, args=[learning_unit_years[1].id]))
        request.user = mock.Mock()

        delete_all_learning_units_year(request, learning_unit_years[1].id)

        self.assertTrue(mock_render.called)
        request, template, context = mock_render.call_args[0]

        self.assertEqual(_('msg_warning_delete_learning_unit') % learning_unit_years[1].learning_unit, context['title'])

        # click on accept button
        request = request_factory.post(reverse(delete_all_learning_units_year, args=[learning_unit_years[1].id]))
        request.user = mock.Mock()
        setattr(request, 'session', 'session')
        setattr(request, '_messages', FallbackStorage(request))

        delete_all_learning_units_year(request, learning_unit_years[1].id)

        msg_level = [m.level for m in get_messages(request)]
        msg = [m.message for m in get_messages(request)]
        self.assertEqual(len(msg), 5)
        self.assertIn(messages.SUCCESS, msg_level)

        for y in range(4):
            with self.assertRaises(ObjectDoesNotExist):
                LearningUnitYear.objects.get(id=learning_unit_years[y].id)

    @mock.patch('django.contrib.auth.decorators')
    @mock.patch('base.views.layout.render')
    def test_delete_from_given_learning_unit_year_case_error(self, mock_render, mock_decorators):
        mock_decorators.login_required = lambda x: x
        mock_decorators.permission_required = lambda *args, **kwargs: lambda func: func

        ly1 = LearningUnitYearFactory()
        LearningUnitEnrollmentFactory(learning_unit_year=ly1)

        from base.views.learning_unit_deletion import delete_from_given_learning_unit_year

        request_factory = RequestFactory()

        request = request_factory.get(reverse(delete_from_given_learning_unit_year, args=[ly1.id]))
        request.user = mock.Mock()

        setattr(request, 'session', 'session')

        delete_from_given_learning_unit_year(request, ly1.id)

        self.assertTrue(mock_render.called)
        request, template, context = mock_render.call_args[0]

        msg = context.get('messages_deletion', [])
        self.assertEqual(_('cannot_delete_learning_unit_year')
                         % {'learning_unit': ly1.acronym,
                            'year': ly1.academic_year},
                         context['title'])

        subtype = _('The partim') if ly1.subtype == learning_unit_year_subtypes.PARTIM else _('The learning unit')
        self.assertIn(_("There is %(count)d enrollments in %(subtype)s %(acronym)s for the year %(year)s")
                      % {'subtype': subtype,
                         'acronym': ly1.acronym,
                         'year': ly1.academic_year,
                         'count': 1},
                      msg)

        self.assertIsNotNone(LearningUnitYear.objects.get(id=ly1.id))

    @mock.patch('django.contrib.auth.decorators')
    @mock.patch('base.views.layout.render')
    def test_delete_all_learning_units_year_case_error(self, mock_render, mock_decorators):
        mock_decorators.login_required = lambda x: x
        mock_decorators.permission_required = lambda *args, **kwargs: lambda func: func

        l1 = LearningUnitFactory()
        ly1 = LearningUnitYearFactory(learning_unit=l1)
        LearningUnitEnrollmentFactory(learning_unit_year=ly1)

        from base.views.learning_unit_deletion import delete_all_learning_units_year

        request_factory = RequestFactory()

        request = request_factory.get(reverse(delete_all_learning_units_year, args=[ly1.id]))
        request.user = mock.Mock()

        setattr(request, 'session', 'session')

        delete_all_learning_units_year(request, ly1.id)

        self.assertTrue(mock_render.called)
        request, template, context = mock_render.call_args[0]

        msg = context.get('messages_deletion', [])
        self.assertEqual(_('cannot_delete_learning_unit')
                         % {'learning_unit': l1.acronym},
                         context['title'])

        subtype = _('The partim') if ly1.subtype == learning_unit_year_subtypes.PARTIM else _('The learning unit')
        self.assertIn(_("There is %(count)d enrollments in %(subtype)s %(acronym)s for the year %(year)s")
                      % {'subtype': subtype,
                         'acronym': ly1.acronym,
                         'year': ly1.academic_year,
                         'count': 1},
                      msg)

        self.assertIsNotNone(LearningUnitYear.objects.get(id=ly1.id))
