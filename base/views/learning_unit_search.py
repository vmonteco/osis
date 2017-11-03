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
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.translation import ugettext_lazy as _
from base import models as mdl
from base.business.learning_unit import get_last_academic_years
from base.forms.common import TooManyResultsException
from base.forms.learning_unit_search import LearningUnitSearchForm
from base.models.enums import learning_container_year_types, learning_unit_year_subtypes
from base.views import layout

SIMPLE_SEARCH = 1
SERVICE_COURSES_SEARCH = 2


@login_required
@permission_required('base.can_access_learningunit', raise_exception=True)
def learning_units(request):
    return _learning_units_search(request, SIMPLE_SEARCH)


@login_required
@permission_required('base.can_access_learningunit', raise_exception=True)
def learning_units_service_course(request):
    return _learning_units_search(request, SERVICE_COURSES_SEARCH)


@login_required
@permission_required('base.can_access_learningunit', raise_exception=True)
def learning_units_activity(request):
    return _learning_units_search(request, SIMPLE_SEARCH)


def _learning_units_search(request, search_type):
    if request.GET.get('academic_year_id'):
        form = LearningUnitSearchForm(request.GET)
    else:
        form = LearningUnitSearchForm()

    found_learning_units = None
    try:
        if form.is_valid():

            if search_type == SIMPLE_SEARCH:
                found_learning_units = form.get_activity_learning_units()
            elif search_type == SERVICE_COURSES_SEARCH:
                found_learning_units = form.get_service_course_learning_units()

            _check_if_display_message(request, found_learning_units)
    except TooManyResultsException:
        messages.add_message(request, messages.ERROR, _('too_many_results'))

    context = {
        'form': form,
        'academic_years': get_last_academic_years(),
        'container_types': learning_container_year_types.LEARNING_CONTAINER_YEAR_TYPES,
        'types': learning_unit_year_subtypes.LEARNING_UNIT_YEAR_SUBTYPES,
        'learning_units': found_learning_units,
        'current_academic_year': mdl.academic_year.current_academic_year(),
        'experimental_phase': True,
        'search_type': search_type
    }
    return layout.render(request, "learning_units.html", context)


def _check_if_display_message(request, found_learning_units):
    if not found_learning_units:
        messages.add_message(request, messages.WARNING, _('no_result'))
    return True
