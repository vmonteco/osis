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
from django.contrib.auth.models import Permission
from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from base.models.enums.academic_calendar_type import EDUCATION_GROUP_EDITION
from base.models.enums.education_group_categories import TRAINING, MINI_TRAINING, GROUP
from base.templatetags.education_group import li_with_deletion_perm, button_with_permission, BUTTON_TEMPLATE, \
    button_order_with_permission, BUTTON_ORDER_TEMPLATE, li_with_create_perm_training, \
    li_with_create_perm_mini_training, li_with_create_perm_group
from base.tests.factories.academic_calendar import AcademicCalendarFactory
from base.tests.factories.authorized_relationship import AuthorizedRelationshipFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.person_entity import PersonEntityFactory

DELETE_MSG = _("delete education group")
PERMISSION_DENIED_MSG = _("The education group edition period is not open.")
UNAUTHORIZED_TYPE_MSG = _("No type of %(category)s can be created as child of %(category)s of type %(type)s")

DISABLED_LI = """
<li class="disabled" id="{}">
    <a href="#" data-toggle="tooltip" title="{}">{}</a>
</li>
"""

ENABLED_LI = """
<li class="" id="{}">
    <a href="{}" data-toggle="tooltip" title="">{}</a>
</li>
"""


class TestEducationGroupTag(TestCase):
    def setUp(self):
        self.education_group_year = EducationGroupYearFactory()
        self.person = PersonFactory()
        PersonEntityFactory(person=self.person, entity=self.education_group_year.management_entity)
        self.url = reverse('delete_education_group', args=[self.education_group_year.id, self.education_group_year.id])

        self.person.user.user_permissions.add(Permission.objects.get(codename="delete_educationgroup"))
        self.person.user.user_permissions.add(Permission.objects.get(codename="change_educationgroup"))
        self.person.user.user_permissions.add(Permission.objects.get(codename="add_educationgroup"))

        self.client.force_login(user=self.person.user)

        self.academic_calendar = AcademicCalendarFactory(
            reference=EDUCATION_GROUP_EDITION,
            start_date=timezone.now(),
            end_date=timezone.now()
        )

        self.context = {
            "person": self.person,
            "education_group_year": self.education_group_year,
            "request": RequestFactory().get("")
        }

    def test_li_with_deletion_perm(self):
        result = li_with_deletion_perm(self.context, self.url, DELETE_MSG)
        self.assertEqual(result, ENABLED_LI.format("link_delete", self.url, DELETE_MSG))

    def test_li_without_deletion_perm(self):
        self.academic_calendar.delete()

        result = li_with_deletion_perm(self.context, self.url, DELETE_MSG)
        self.assertEqual(result, DISABLED_LI.format("link_delete", PERMISSION_DENIED_MSG, DELETE_MSG))

    def test_button_with_permission(self):
        result = button_with_permission(self.context, "title", "id", "edit")
        self.assertEqual(result, BUTTON_TEMPLATE.format("title", "id", "", "fa-edit"))

    def test_a_without_permission(self):
        self.academic_calendar.delete()

        result = button_with_permission(self.context, "title", "id", "edit")
        self.assertEqual(result, BUTTON_TEMPLATE.format(PERMISSION_DENIED_MSG, "id", "disabled", "fa-edit"))

    def test_button_order_with_permission(self):
        result = button_order_with_permission(self.context, "title", "id", "edit")
        self.assertEqual(result, BUTTON_ORDER_TEMPLATE.format("title", "id", "edit", "", "fa-edit"))

    def test__without_permission(self):
        self.academic_calendar.delete()

        result = button_order_with_permission(self.context, "title", "id", "edit")
        self.assertEqual(result,
                         BUTTON_ORDER_TEMPLATE.format(PERMISSION_DENIED_MSG, "id", "edit", "disabled", "fa-edit"))

    def test_li_with_create_perm_training(self):
        relation = AuthorizedRelationshipFactory(parent_type=self.education_group_year.education_group_type)
        relation.child_type.category = TRAINING
        relation.child_type.save()

        result = li_with_create_perm_training(self.context, self.url, "")
        self.assertHTMLEqual(result, ENABLED_LI.format("link_create", self.url, ""))

    def test_li_with_create_perm_mini_training(self):
        relation = AuthorizedRelationshipFactory(parent_type=self.education_group_year.education_group_type)
        relation.child_type.category = MINI_TRAINING
        relation.child_type.save()

        result = li_with_create_perm_mini_training(self.context, self.url, "")
        self.assertHTMLEqual(result, ENABLED_LI.format("link_create", self.url, ""))

    def test_li_with_create_perm_group(self):
        relation = AuthorizedRelationshipFactory(parent_type=self.education_group_year.education_group_type)
        relation.child_type.category = GROUP
        relation.child_type.save()

        result = li_with_create_perm_group(self.context, self.url, "")
        self.assertHTMLEqual(result, ENABLED_LI.format("link_create", self.url, ""))

    def test_li_with_create_perm_training_disabled(self):
        result = li_with_create_perm_training(self.context, self.url, "")

        msg = UNAUTHORIZED_TYPE_MSG % {
            "category": _(self.education_group_year.education_group_type.category),
            "type": self.education_group_year.education_group_type.name
        }
        self.assertHTMLEqual(result, DISABLED_LI.format("link_create", msg, ""))

    def test_li_with_create_perm_mini_training_disabled(self):
        result = li_with_create_perm_mini_training(self.context, self.url, "")
        msg = UNAUTHORIZED_TYPE_MSG % {
            "category": _(self.education_group_year.education_group_type.category),
            "type": self.education_group_year.education_group_type.name
        }
        self.assertHTMLEqual(result, DISABLED_LI.format("link_create", msg, ""))

    def test_li_with_create_perm_group_disabled(self):
        result = li_with_create_perm_group(self.context, self.url, "")
        msg = UNAUTHORIZED_TYPE_MSG % {
            "category": _(self.education_group_year.education_group_type.category),
            "type": self.education_group_year.education_group_type.name
        }
        self.assertHTMLEqual(result, DISABLED_LI.format("link_create", msg, ""))
