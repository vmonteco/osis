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
from django.core.exceptions import ImproperlyConfigured

from RulesManagement.models import FieldReference


class ModelFormMixin:

    def disable_field(self, field_name):
        field = self.fields[field_name]
        field.disabled = True
        field.required = False


class PermissionFieldMixin(ModelFormMixin):
    """
    Mixin to connect to form

    It enables/disables fields according to permissions and the context
    """
    model_permission = FieldReference
    context = ""

    def __init__(self, *args, user=None, **kwargs):
        if not user:
            raise ImproperlyConfigured("This form must receive the user to determine his permissions")

        if "context" in kwargs:
            self.context = kwargs.pop("context")

        self.user = user
        super().__init__(*args, **kwargs)

        self.user_permissions = Permission.objects.filter(user=self.user)

        # Check permissions for all matching fields
        for field_ref in self.get_queryset():
            field_name = field_ref.field_name
            if field_name in self.fields and not self.check_user_permission(field_ref):
                self.disable_field(field_name)

    def check_user_permission(self, field_reference):
        # If a context has been set, it must match with the reference to check the permission
        if field_reference.context and field_reference.context != self.get_context():
            return True

        for perm in field_reference.permissions.all():
            if perm in self.user_permissions:
                return True
        return False

    def get_queryset(self):
        return self.model_permission.objects.filter(
            content_type__app_label=self._meta.model._meta.app_label,
            content_type__model=self._meta.model._meta.model_name
        )

    def get_context(self):
        """
        Can be override to use a specific context according to business
        :return: self.context
        """
        return self.context
