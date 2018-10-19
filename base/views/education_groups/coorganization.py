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

from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse

from base.models.education_group_year import EducationGroupYear
from base.models.education_group_organization import EducationGroupOrganization
from base.forms.education_group.organization import OrganizationEditForm
from base.views import layout
from base.views.mixins import AjaxTemplateMixin
from django.views.generic import UpdateView
from django.views.generic.detail import SingleObjectMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.utils.translation import ugettext_lazy as _

HTML_ANCHOR = "#coorganization_id_"
HTML_ANCHOR_TABLE_COORGANIZATIONS = "#tbl_coorganization"


class UpdateEducationGroupOrganizationView(AjaxTemplateMixin, SuccessMessageMixin, UpdateView):
    # SingleObjectMixin
    model = EducationGroupOrganization
    context_object_name = "coorganization"
    pk_url_kwarg = 'coorganization_id'
    # UpdateView
    form_class = OrganizationEditForm
    template_name = "education_group/organization_edit.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["education_group_yr"] = self.kwargs["education_group_year_id"]
        return kwargs

    def get_success_message(self, cleaned_data):
        return _("The coorganization modifications has been saved")

    def get_success_url(self):
        return reverse("education_group_read", args=[self.kwargs["root_id"], self.object.education_group_year.pk])


@login_required
@permission_required('base.can_access_education_group', raise_exception=True)
def create(request, root_id, education_group_year_id):
    education_group_yr = get_object_or_404(EducationGroupYear, pk=education_group_year_id)

    form = OrganizationEditForm(request.POST or None, education_group_yr=education_group_yr)

    if form.is_valid():
        return _save_and_redirect(form, root_id, education_group_year_id)
    context = {'education_group_year': education_group_yr,
               'root_id': root_id,
               'form': form,
               'create': True}

    return layout.render(request, "education_group/organization_edit.html", context)


def _save_and_redirect(form, root_id, education_group_year_id):
    co_organization = form.save_co_organization(education_group_year_id)
    return HttpResponseRedirect(reverse('education_group_read',
                                        kwargs={'root_id': root_id,
                                                'education_group_year_id': education_group_year_id}) + "{}{}".format(
        HTML_ANCHOR,
        co_organization.id))


@login_required
@permission_required('base.can_access_education_group', raise_exception=True)
def delete(request, root_id, education_group_year_id):
    co_organization_id = request.POST.get('co_organization_id_to_delete')
    education_group_organization = get_object_or_404(EducationGroupOrganization, pk=co_organization_id)
    education_group_organization.delete()
    return HttpResponseRedirect(reverse('education_group_read',
                                        kwargs={'root_id': root_id,
                                                'education_group_year_id': education_group_year_id}) + "{}".format(
        HTML_ANCHOR_TABLE_COORGANIZATIONS))
