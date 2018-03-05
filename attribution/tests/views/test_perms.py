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
from unittest import mock

from django.core.exceptions import PermissionDenied
from django.http import HttpRequest
from django.test import SimpleTestCase

from attribution.views.perms import tutor_can_edit_educational_information


def create_request_object_with_none_user():
    req_object = HttpRequest()
    req_object.__setattr__("user", None)
    return req_object


def pass_view_func_to_tutor_can_edit_educational_information():
    view_func = lambda req, luy_id: True
    return  tutor_can_edit_educational_information(view_func)


class TestTutorCanEditEducationalInformation(SimpleTestCase):
    @mock.patch("attribution.views.perms.can_user_edit_educational_information", side_effect=lambda req, luy_id: False)
    def test_when_cannot_edit(self, mock_can_user_edit_educational_information):
        perm_f = pass_view_func_to_tutor_can_edit_educational_information()
        with self.assertRaises(PermissionDenied):
            req_object = create_request_object_with_none_user()
            perm_f(req_object, 45)
        self.assertTrue(mock_can_user_edit_educational_information.called)

    @mock.patch("attribution.views.perms.can_user_edit_educational_information", side_effect=lambda req, luy_id: True)
    def test_when_can_edit(self, mock_can_user_edit_educational_information):
        perm_f = pass_view_func_to_tutor_can_edit_educational_information()
        req_object = create_request_object_with_none_user()
        self.assertTrue(perm_f(req_object, 45))
        self.assertTrue(mock_can_user_edit_educational_information.called)
