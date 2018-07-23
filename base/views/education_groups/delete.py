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
from django.urls import reverse_lazy
from django.utils.translation import ngettext_lazy
from django.utils.translation import ugettext_lazy as _

from base.models.education_group_year import EducationGroupYear
from base.models.group_element_year import GroupElementYear
from base.models.offer_enrollment import OfferEnrollment
from base.views.common_classes import DeleteViewWithDependencies
from base.views.education_groups.perms import can_delete_education_group


class DeleteGroupEducationYearView(DeleteViewWithDependencies):
    # DeleteView
    model = EducationGroupYear
    success_url = reverse_lazy('education_groups')
    pk_url_kwarg = "education_group_year_id"
    template_name = "education_group/delete.html"
    context_object_name = "education_group_year"

    # RulesRequiredMixin
    raise_exception = True
    rules = [can_delete_education_group]

    # DeleteViewWithDependencies
    success_message = "The education group has been deleted."
    protected_template = "education_group/protect_delete.html"

    # FlagMixin
    flag = 'education_group_delete'

    # TODO : This method is a quick fix.
    # GroupElementYear should be split in two tables with their own protected FK !
    def post_collect(self):
        for instance, obj in self.collector.model_objs.items():
            if instance is GroupElementYear:
                self._append_protected_object(obj)

    def _append_protected_object(self, list_objects):
        if not isinstance(list_objects, (list, set)):
            list_objects = [list_objects]

        for obj in list_objects:
            if not obj.is_deletable():
                self.collector.protected.add(obj)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.collector.protected:
            context["protected_messages"] = self.get_protected_messages()

        return context

    def get_protected_messages(self):
        protected_message = []

        count_enrollment = len([
            enrollment for enrollment in self.collector.protected if isinstance(enrollment, OfferEnrollment)
        ])

        if count_enrollment:
            protected_message.append(
                ngettext_lazy(
                    "%(count_enrollment)d student is  enrolled in the offer.",
                    "%(count_enrollment)d students are  enrolled in the offer.",
                    count_enrollment
                ) % {"count_enrollment": count_enrollment}
            )

        if [isinstance(group, GroupElementYear) for group in self.collector.protected]:
            protected_message.append(_("The content of the education group is not empty."))

        return protected_message
