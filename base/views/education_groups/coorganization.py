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
import abc
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import UpdateView, CreateView
from django.contrib.messages.views import SuccessMessageMixin
from django.utils.translation import ugettext_lazy as _
from django.utils.functional import cached_property
from django.utils.decorators import method_decorator

from base.models.education_group_year import EducationGroupYear
from base.models.education_group_organization import EducationGroupOrganization
from base.forms.education_group.organization import OrganizationEditForm
from base.views.mixins import AjaxTemplateMixin
from base.views.education_groups import perms
from base.views.mixins import RulesRequiredMixin


class CreateEducationGroupOrganizationView(RulesRequiredMixin, AjaxTemplateMixin, SuccessMessageMixin, CreateView):
    model = EducationGroupOrganization
    context_object_name = "coorganization"

    form_class = OrganizationEditForm
    template_name = "education_group/organization_edit.html"

    # RulesRequiredMixin
    raise_exception = True

    rules = [perms.can_change_education_group]

    def _call_rule(self, rule):
        return rule(self.person.user, self.education_group_year)

    @cached_property
    def person(self):
        return self.request.user.person

    @cached_property
    def education_group_year(self):
        return get_object_or_404(EducationGroupYear, pk=self.kwargs['education_group_year_id'])

    def get_success_message(self, cleaned_data):
        return _("The coorganization has been created")

    def get_success_url(self):
        return reverse("education_group_read", args=[self.kwargs["root_id"], self.object.education_group_year.pk])

    def form_valid(self, form):
        form.instance.education_group_year = self.education_group_year
        return super().form_valid(form)


class UpdateEducationGroupOrganizationView(RulesRequiredMixin, AjaxTemplateMixin, SuccessMessageMixin, UpdateView):

    model = EducationGroupOrganization
    context_object_name = "coorganization"
    pk_url_kwarg = 'coorganization_id'

    form_class = OrganizationEditForm
    template_name = "education_group/organization_edit.html"

    # RulesRequiredMixin
    raise_exception = True
    rules = [perms.can_change_education_group]

    def _call_rule(self, rule):
        return rule(self.person.user, self.education_group_year)

    @cached_property
    def person(self):
        return self.request.user.person

    @cached_property
    def education_group_year(self):
        return get_object_or_404(EducationGroupYear, pk=self.kwargs['education_group_year_id'])

    def get_success_message(self, cleaned_data):
        return _("The coorganization modifications has been saved")

    def get_success_url(self):
        return reverse("education_group_read", args=[self.kwargs["root_id"],
                                                     self.object.education_group_year.pk])


@login_required
@permission_required('base.can_access_education_group', raise_exception=True)
def delete(request, root_id, education_group_year_id):
    co_organization_id = request.POST.get('co_organization_id_to_delete')
    education_group_organization = get_object_or_404(EducationGroupOrganization, pk=co_organization_id)
    education_group_organization.delete()
    return HttpResponseRedirect(reverse('education_group_read',
                                        kwargs={'root_id': root_id,
                                                'education_group_year_id': education_group_year_id}) + "{}".format(
        "#tbl_coorganization"))
