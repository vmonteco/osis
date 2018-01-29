#############################################################################
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
from django.test.client import RequestFactory
from django.test.testcases import TestCase
from unittest import mock

from django.urls.base import reverse

from base.tests.factories.person import PersonFactory
from base.tests.factories.user import SuperUserFactory
from osis_common.models import message_history
from django.test.utils import override_settings
from django.utils import translation

LANGUAGE_CODE_FR = 'fr-be'
LANGUAGE_CODE_EN = 'en'


class MyOsisViewTestCase(TestCase):

    fixtures = ['osis_common/fixtures/messages_tests.json']

    def setUp(self):
        self.a_superuser = SuperUserFactory()
        self.person = PersonFactory(user=self.a_superuser,
                                    language=LANGUAGE_CODE_FR)
        self.client.force_login(self.a_superuser)
        self.requestFactory = RequestFactory()

    @mock.patch('django.contrib.auth.decorators')
    @mock.patch('base.views.layout.render')
    def test_my_osis_index(self, mock_render, mock_decorators):
        mock_decorators.login_required = lambda x: x
        mock_decorators.permission_required = lambda *args, **kwargs: lambda func: func

        from base.views.my_osis import my_osis_index

        request = self.requestFactory.get(reverse(my_osis_index))
        request.user = mock.Mock()
        my_osis_index(request)
        self.assertTrue(mock_render.called)
        request, template, context = mock_render.call_args[0]
        self.assertEqual(template, 'my_osis/home.html')

    def test_my_messages_index(self):
        from base.views.my_osis import my_messages_index

        response = self.client.get(reverse(my_messages_index))

        self.assertEqual(response.status_code, 200)
        template = response.templates[0].name
        self.assertEqual(template, 'my_osis/my_messages.html')

    def test_get_messages_formset(self):
        messages = message_history.MessageHistory.objects.all()
        from base.views.my_osis import get_messages_formset
        formset_factory_result = get_messages_formset(messages)
        self.assertEqual(len(messages), len(formset_factory_result))

    @mock.patch('base.views.layout.render')
    def test_profile(self, mock_render):
        request = self.get_request()
        from base.views.my_osis import profile

        profile(request)

        self.assertTrue(mock_render.called)
        request, template, context = mock_render.call_args[0]

        self.assertEqual(template, 'my_osis/profile.html')
        with self.assertRaises(KeyError):
            context['tab_attribution_on']

    @mock.patch('base.views.layout.render')
    def test_profile_attributions(self, mock_render):
        request = self.get_request()
        from base.views.my_osis import profile_attributions

        profile_attributions(request)

        self.assertTrue(mock_render.called)
        request, template, context = mock_render.call_args[0]

        self.assertEqual(template, 'my_osis/profile.html')
        self.assertEqual(context['tab_attribution_on'], True)

    @mock.patch('base.views.layout.render')
    def test_read_message(self, mock_render):
        message = self.get_message()
        request = self.get_request()
        from base.views.my_osis import read_message

        read_message(request, message.id)

        self.assertTrue(mock_render.called)
        request, template, context = mock_render.call_args[0]

        self.assertEqual(template, 'my_osis/my_message.html')
        self.assertEqual(context['my_message'], message)


    def test_get_data(self):
        request = self.get_request()
        from base.views.my_osis import _get_data

        data = _get_data(request)
        self.assertEqual(data['person'], self.person)

    @mock.patch('base.views.layout.render')
    @override_settings(LANGUAGES=[('fr-be', 'French'), ('en', 'English'), ], LANGUAGE_CODE='fr-be')
    def test_profile_lang(self, mock_render):

        data = {
            "ui_language": LANGUAGE_CODE_EN
        }
        request_factory = RequestFactory()
        request = request_factory.post(reverse('profile_lang'), data)
        request.user = self.a_superuser

        request.session = {translation.LANGUAGE_SESSION_KEY: LANGUAGE_CODE_FR}
        from base.views.my_osis import profile_lang

        response = profile_lang(request)

        self.assertTrue(mock_render.called)
        request, template, context = mock_render.call_args[0]

        self.assertEqual(template, 'my_osis/profile.html')
        self.assertEqual(context['person'].language, LANGUAGE_CODE_EN)

    def get_request(self):
        request_factory = RequestFactory()
        request = request_factory.get(reverse('home'))
        request.user = self.a_superuser
        return request

    def get_message(self):
        messages = message_history.MessageHistory.objects.all()
        message = messages[0]
        return message
