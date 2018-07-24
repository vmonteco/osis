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

    """
        {% for elem in parent.children_by_group_element_year %}
        <li>{{ elem.child.title }} ({% if elem.relative_credits %}{{ elem.relative_credits }}{% else %}{{ elem.child.credits|default_if_none:'0' }}{% endif %} {% trans 'credits'|lower %})</li>
        {% if elem.child.children_by_group_element_year %}
            {% include "education_group/blocks/pdf_branch.html" with parent=elem.child %}
        {% endif %}
    {% endfor %}
    
    
    
    """

    root = []

    root.append(get_children(parent))





    # return Render.render('education_group/pdf_content.html', {'parent': parent})
    return layout.render(request, 'education_group/pdf_content.html', {'parent': parent})


def get_children(parent):
    root = []
    child_with_egy = parent.groupelementyear_set.filter(child_branch__isnull=False)
    child_with_luy = parent.groupelementyear_set.filter(child_leaf__isnull=False)

    for group_element_year in child_with_egy:
        root.append(get_children(group_element_year.child_branch))

    return root
