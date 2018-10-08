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
from django.test import TestCase

from base.tests.factories.user import UserFactory
from base.utils.cache import cache
from base.utils.notifications import make_notifications_cache_key, are_notifications_already_loaded


class TestNotificationsBaseClass(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_without_data = UserFactory()
        cls.user_with_data = UserFactory()
        cls.user_with_empty_data = UserFactory()

        cls.notifications = ["Notif 1", "Notif 2", "Notif 3"]

    def setUp(self):
        self.set_cache_data(self.user_with_data, self.notifications)
        self.set_cache_data(self.user_with_empty_data, [])

    def set_cache_data(self, user, data):
        cache_key = make_notifications_cache_key(user)
        cache.set(cache_key, data)

    def tearDown(self):
        cache.clear()


class TestAreNotificationsAlreadyLoaded(TestNotificationsBaseClass):
    def test_return_false_when_key_user_data_not_in_cache(self):
        self.assertFalse(are_notifications_already_loaded(self.user_without_data))

    def test_return_true_when_empty_data_in_cache(self):
        self.assertTrue(are_notifications_already_loaded(self.user_with_empty_data))

    def test_return_true_when_data_in_cache(self):
        self.assertTrue(are_notifications_already_loaded(self.user_with_data))