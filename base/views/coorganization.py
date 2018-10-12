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

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

from base.models.education_group_year import EducationGroupYear
from base.forms.education_group.coorganization import CoorganizationEditForm
from . import layout
from django.http import HttpResponseRedirect
from django.urls import reverse
HTML_ANCHOR = "#coorganization_id_"


@login_required
def create(request, root_id, education_group_year_id):
    education_group_yr = get_object_or_404(EducationGroupYear, pk=education_group_year_id)

    form = CoorganizationEditForm(request.POST or None,
                                  initial={'education_group_year': education_group_yr})

    if form.is_valid():
        return _save_and_redirect(form, root_id, education_group_year_id)

    context = {'education_group_year': education_group_yr,
               'root_id': root_id,
               'form': form,
               'create': True}

    return layout.render(request, "education_group/coorganization_edit.html", context)


def _save_and_redirect(form, root_id, education_group_year_id):
    coorganization = form.save()
    return HttpResponseRedirect(reverse('education_group_read',
                                        kwargs={'root_id': root_id,
                                                'education_group_year_id': education_group_year_id}) + "{}{}".format(
        HTML_ANCHOR,
        coorganization.id))
