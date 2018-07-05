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
from django.contrib.admin.utils import NestedObjects
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.utils.encoding import force_text
from django.utils.text import capfirst
from django.views.generic import DeleteView

from base.views.common import display_success_messages


class DeleteViewWithDependencies(PermissionRequiredMixin, DeleteView):
    collector = NestedObjects(using="default")

    success_message = "The objects are been deleted successfully"
    protected_template = None

    def get(self, request, *args, **kwargs):
        # Collect objects how will be deleted
        self.collector.collect([self.get_object()])
        self.post_collect()

        # If there is some protected objects, change the template
        if self.collector.protected:
            self.template_name = self.protected_template

        return super().get(request, *args, **kwargs)

    def post_collect(self):
        pass

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["deletable_objects"] = self.collector.nested(format_callback)
        context["protected_objects"] = self.collector.protected
        return context

    def delete(self, request, *args, **kwargs):
        result = super().delete(request, *args, **kwargs)
        display_success_messages(request, self.success_message)
        return result


def format_callback(obj):
    return "%s: %s" % (capfirst(obj._meta.verbose_name), force_text(obj))
