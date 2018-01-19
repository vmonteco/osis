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
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.decorators.http import require_http_methods

from attribution import models as mdl_attr
from attribution.business.attribution import get_attributions_list, _set_summary_responsible_to_true
from attribution.business.entity_manager import _append_entity_version
from attribution.business.summary_responsible import get_learning_unit_year_managed_by_user_from_request, \
    find_attributions_based_on_request_criterias
from base import models as mdl_base
from base.models.entity_manager import is_entity_manager
from base.views import layout


@login_required
@user_passes_test(is_entity_manager)
def search(request):
    entities_manager = mdl_base.entity_manager.find_by_user(request.user)
    academic_year = mdl_base.academic_year.current_academic_year()
    _append_entity_version(entities_manager, academic_year)
    context = {"entities_manager": entities_manager,
               "academic_year": academic_year,
               "init": "0"}
    if request.GET:
        attributions = find_attributions_based_on_request_criterias(entities_manager, request)
        context.update({"dict_attribution": get_attributions_list(attributions, "-summary_responsible"),
                        "learning_unit_title": request.GET.get('learning_unit_title'),
                        "course_code": request.GET.get('course_code'),
                        "tutor": request.GET.get('tutor'),
                        "summary_responsible": request.GET.get('summary_responsible'),
                        "init": "1"})

    return layout.render(request, 'summary_responsible.html', context)


@login_required
@user_passes_test(is_entity_manager)
def edit(request):
    a_learning_unit_year = get_learning_unit_year_managed_by_user_from_request(request)
    context = {
        'learning_unit_year': a_learning_unit_year,
        'attributions': mdl_attr.attribution.find_all_responsible_by_learning_unit_year(a_learning_unit_year),
        'academic_year': mdl_base.academic_year.current_academic_year(),
        'course_code': request.GET.get('course_code'),
        'learning_unit_title': request.GET.get('learning_unit_title'),
        'tutor': request.GET.get('tutor'),
        'summary_responsible': request.GET.get('summary_responsible')
    }
    return layout.render(request, 'summary_responsible_edit.html', context)


@login_required
@require_http_methods(['POST'])
@user_passes_test(is_entity_manager)
def update(request, pk):
    if request.POST.get('action') == "update":
        mdl_attr.attribution.clear_summary_responsible_by_learning_unit_year(pk)
        if request.POST.get('attribution'):
            attribution_id = request.POST.get('attribution').strip('attribution_')
            attribution = mdl_attr.attribution.find_by_id(attribution_id)
            attributions = mdl_attr.attribution.search(tutor=attribution.tutor,
                                                       learning_unit_year=attribution.learning_unit_year)
            _set_summary_responsible_to_true(attributions)

    return HttpResponseRedirect("{}?course_code={}&learning_unit_title={}&tutor={}&summary_responsible={}"
                                .format(reverse('summary_responsible'),
                                        request.POST.get('course_code', ''),
                                        request.POST.get('learning_unit_title', ''),
                                        request.POST.get('tutor', ''),
                                        request.POST.get('summary_responsible', ''))
                                )
