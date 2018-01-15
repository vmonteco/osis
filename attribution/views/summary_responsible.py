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
from django.contrib.auth.decorators import login_required, user_passes_test

from attribution import models as mdl_attr
from attribution.business.attribution import get_attributions_list
from attribution.business.entity_manager import _append_entity_version
from base import models as mdl_base
from base.models.entity_manager import is_entity_manager
from base.views import layout


@login_required
@user_passes_test(is_entity_manager)
def search(request):
    entities_manager = mdl_base.entity_manager.find_by_user(request.user)
    academic_year = mdl_base.academic_year.current_academic_year()
    _append_entity_version(entities_manager, academic_year)
    if request.GET:
        entities = [entity_manager.entity for entity_manager in entities_manager]
        entities_with_descendants = mdl_base.entity.find_descendants(entities)
        attributions = list(mdl_attr.attribution.search_summary_responsible(
            learning_unit_title=request.GET.get('learning_unit_title'),
            course_code=request.GET.get('course_code'),
            entities=entities_with_descendants,
            tutor=request.GET.get('tutor'),
            responsible=request.GET.get('summary_responsible')
        ))
        dict_attribution = get_attributions_list(attributions)
        return layout.render(request, 'summary_responsible.html',
                             {"entities_manager": entities_manager,
                              "academic_year": academic_year,
                              "dict_attribution": dict_attribution,
                              "learning_unit_title": request.GET.get('learning_unit_title'),
                              "course_code": request.GET.get('course_code'),
                              "tutor": request.GET.get('tutor'),
                              "summary_responsible": request.GET.get('summary_responsible'),
                              "init": "1"})
    else:
        return layout.render(request, 'summary_responsible.html',
                             {"entities_manager": entities_manager,
                              "academic_year": academic_year,
                              "init": "0"})

@login_required
@user_passes_test(is_entity_manager)
def edit(request):
    pass
