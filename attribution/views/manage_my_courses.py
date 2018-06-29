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
from django.urls import reverse

from attribution.views.perms import tutor_can_view_educational_information
from base.business.learning_units.perms import is_eligible_to_update_learning_unit_pedagogy, \
    find_educational_information_submission_dates_of_learning_unit_year
from base.models.learning_unit_year import find_tutor_learning_unit_years
from attribution.models.attribution import find_all_summary_responsibles_by_learning_unit_years

from base.models import academic_year, entity_calendar
from base.models.enums import academic_calendar_type
from base.models.learning_unit_year import LearningUnitYear
from base.models.tutor import Tutor
from base.views import layout
from base.views.learning_units.pedagogy.update import update_learning_unit_pedagogy, edit_learning_unit_pedagogy
from base.views.learning_units.perms import PermissionDecorator


@login_required
def list_my_attributions_summary_editable(request):
    tutor = get_object_or_404(Tutor, person__user=request.user)
    tutor_learning_unit_years = find_tutor_learning_unit_years(tutor=tutor)

    score_responsibles = find_all_summary_responsibles_by_learning_unit_years(tutor_learning_unit_years)

    entity_calendars = entity_calendar.build_calendar_by_entities(
        ac_year=academic_year.current_academic_year(),
        reference=academic_calendar_type.SUMMARY_COURSE_SUBMISSION
    )

    context = {
        'learning_unit_years_summary_editable': tutor_learning_unit_years,
        'entity_calendars': entity_calendars,
        'score_responsibles': score_responsibles
    }
    return layout.render(request, 'manage_my_courses/list_my_courses_summary_editable.html', context)


@login_required
@tutor_can_view_educational_information
def view_educational_information(request, learning_unit_year_id):
    context = {
        'submission_dates': find_educational_information_submission_dates_of_learning_unit_year(
                learning_unit_year_id)
    }
    template = 'manage_my_courses/educational_information.html'
    return update_learning_unit_pedagogy(request, learning_unit_year_id, context, template)


@login_required
@PermissionDecorator(is_eligible_to_update_learning_unit_pedagogy, "learning_unit_year_id", LearningUnitYear)
def edit_educational_information(request, learning_unit_year_id):
    redirect_url = reverse(view_educational_information, kwargs={'learning_unit_year_id': learning_unit_year_id})
    return edit_learning_unit_pedagogy(request, learning_unit_year_id, redirect_url)
