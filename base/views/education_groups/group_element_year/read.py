##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2017 Université catholique de Louvain (http://www.uclouvain.be)
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
from base.views import layout


@login_required
def pdf_content(request, education_group_year_id):
    parent = get_object_or_404(EducationGroupYear, pk=education_group_year_id)

    return layout.render(request, 'education_group/pdf_content.html', {'tree': get_verbose_children(parent)})


def get_verbose_children(parent):
    result = []

    for group_element_year in parent.children:
        result.append(group_element_year.verbose)
        print(group_element_year.verbose)

        if group_element_year.child_branch:
            result.append(get_verbose_children(group_element_year.child_branch))

    return result
