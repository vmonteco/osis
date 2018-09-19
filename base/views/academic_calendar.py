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
import datetime

from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404
from django.urls import reverse

from base import models as mdl
from base.forms.academic_calendar import AcademicCalendarForm
from base.models.academic_calendar import AcademicCalendar
from base.models.enums import academic_calendar_type
from base.models.enums.academic_calendar_type import ACADEMIC_CATEGORY, PROJECT_CATEGORY
from base.models.utils.utils import get_object_or_none
from . import layout


def _build_gantt_json(academic_calendar_list, show_academic_events, show_project_events):
    academic_calendar_data = []
    for calendar in academic_calendar_list:
        category = calendar.get_category()

        if _item_must_be_skipped(calendar, category, show_academic_events, show_project_events):
            continue

        data = {
            'id': calendar.pk,
            'text': calendar.title,
            'start_date': calendar.start_date.strftime('%d-%m-%Y'),
            'end_date': calendar.end_date.strftime('%d-%m-%Y'),
            'color': academic_calendar_type.CALENDAR_TYPES_COLORS.get(calendar.reference, '#337ab7'),
            'progress': _compute_progress(calendar),
            'category': category,
        }
        academic_calendar_data.append(data)
    return {
        "data": academic_calendar_data
    }


def _compute_progress(calendar):
    today = datetime.date.today()
    if today <= calendar.start_date:
        progress = 0
    elif calendar.start_date < today < calendar.end_date:
        progress = (today - calendar.start_date) / (calendar.end_date - calendar.start_date)
    else:
        progress = 1
    return progress


def _item_must_be_skipped(calendar, category, show_academic_events, show_project_events):
    return calendar.start_date is None or \
        calendar.end_date is None or \
        (category == ACADEMIC_CATEGORY and not show_academic_events) or \
        (category == PROJECT_CATEGORY and not show_project_events)


def _get_undated_calendars(academic_calendar_list):
    undated_calendars_list = []
    for calendar in academic_calendar_list:
        if calendar.start_date is None or calendar.end_date is None:
            undated_calendars_list.append(calendar)
    return undated_calendars_list


@login_required
@permission_required('base.can_access_academic_calendar', raise_exception=True)
def academic_calendars(request):
    academic_year = request.GET.get('academic_year') or mdl.academic_year.starting_academic_year().pk
    academic_year = int(academic_year)
    academic_years = mdl.academic_year.find_academic_years()

    show_academic_events = request.GET.get('show_academic_events')
    show_project_events = request.GET.get('show_project_events') and request.user.is_superuser

    academic_calendar_list = mdl.academic_calendar.find_academic_calendar_by_academic_year(academic_year)
    academic_calendar_json = _build_gantt_json(academic_calendar_list, show_academic_events, show_project_events)
    undated_calendars_list = _get_undated_calendars(academic_calendar_list)
    show_gantt_diagram = bool(len(academic_calendar_json['data']))

    return layout.render(
        request,
        "academic_calendars.html",
        {
            'academic_year': academic_year,
            'academic_years': academic_years,
            'show_academic_events': show_academic_events,
            'show_project_events': show_project_events,
            'academic_calendar_json': academic_calendar_json,
            'undated_calendars_list': undated_calendars_list,
            'show_gantt_diagram': show_gantt_diagram,
        }
    )


@login_required
@permission_required('base.can_access_academic_calendar', raise_exception=True)
def academic_calendar_read(request, academic_calendar_id):
    academic_calendar = get_object_or_404(mdl.academic_calendar.AcademicCalendar, pk=academic_calendar_id)
    return layout.render(
        request,
        "academic_calendar.html",
        {
            'academic_calendar': academic_calendar,
            'url_academic_calendars': build_url_academic_calendars(request),
        }
    )


@login_required
@permission_required('base.can_access_academic_calendar', raise_exception=True)
def academic_calendar_form(request, academic_calendar_id):
    academic_calendar = get_object_or_none(AcademicCalendar, pk=academic_calendar_id)

    if request.method == 'GET':
        academic_cal_form = AcademicCalendarForm(instance=academic_calendar)
    else:
        academic_cal_form = AcademicCalendarForm(data=request.POST, instance=academic_calendar)

        if academic_cal_form.is_valid():
            academic_cal_form.save()
            return academic_calendar_read(request, academic_cal_form.instance.id)
    return layout.render(
        request,
        "academic_calendar_form.html",
        {
            'form': academic_cal_form,
            'url_academic_calendars': build_url_academic_calendars(request),
        }
    )


def build_url_academic_calendars(request):
    url_academic_calendars = reverse('academic_calendars') + "?show_academic_events=on"
    if request.user.is_superuser:
        url_academic_calendars += "&show_project_events=on"

    return url_academic_calendars
